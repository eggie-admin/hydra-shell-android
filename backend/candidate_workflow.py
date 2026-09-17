from __future__ import annotations

import hashlib
import json
import os
import secrets
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

HOST = "127.0.0.1"
PORT = int(os.environ.get("LUHM_MUTATION_PORT", "8790"))
REPO_ROOT = Path(os.environ.get("LUHM_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()
STATE_ROOT = Path(os.environ.get("LUHM_MUTATION_STATE", Path.home() / ".local/state/luhm-mutation")).expanduser().resolve()
WEB_ROOT = Path(__file__).resolve().parent / "web"
MAX_CONTENT_BYTES = int(os.environ.get("LUHM_MUTATION_MAX_BYTES", str(1024 * 1024)))
DENIED_PARTS = {".git", ".secrets", "secrets", "secret", "credentials", "private_keys"}
DENIED_NAMES = {".env", "id_rsa", "id_ed25519", "authorized_keys"}

app = Flask(__name__)
_stages: dict[str, "MutationStage"] = {}


@dataclass
class MutationStage:
    stage_id: str
    approval_token: str
    path: str
    expected_sha256: str | None
    proposed_sha256: str
    content: str
    created_at: str
    status: str = "STAGED_AWAITING_HUMAN_APPROVAL"

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("content", None)
        data.pop("approval_token", None)
        return data


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_repo_path(relative_path: str) -> Path:
    value = relative_path.strip().replace("\\", "/")
    if not value or value.startswith("/"):
        raise ValueError("path must be repo-relative")
    parts = Path(value).parts
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("path traversal is not allowed")
    lowered = {part.lower() for part in parts}
    if lowered & DENIED_PARTS or Path(value).name.lower() in DENIED_NAMES:
        raise ValueError("path is protected by the mutation boundary")
    target = (REPO_ROOT / value).resolve()
    try:
        target.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("path escapes repository root") from exc
    return target


def current_sha(target: Path) -> str | None:
    return sha256_bytes(target.read_bytes()) if target.exists() else None


def checkpoint(stage: MutationStage, target: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    checkpoint_dir = STATE_ROOT / "checkpoints" / f"{stamp}-{stage.stage_id}"
    checkpoint_dir.mkdir(parents=True, exist_ok=False)
    metadata = {
        "stage_id": stage.stage_id,
        "path": stage.path,
        "expected_sha256": stage.expected_sha256,
        "proposed_sha256": stage.proposed_sha256,
        "created_at": stage.created_at,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "preimage_exists": target.exists(),
    }
    (checkpoint_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    if target.exists():
        (checkpoint_dir / "preimage.bin").write_bytes(target.read_bytes())
    return checkpoint_dir


def atomic_write(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        tmp_name = handle.name
    os.replace(tmp_name, target)


@app.get("/")
def candidate_ui():
    return send_from_directory(WEB_ROOT, "mutation-candidate.html")


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "luhm-local-mutation-candidate",
            "repo_root": str(REPO_ROOT),
            "write_primitive": "utf8_file_replace_only",
            "shell_execution": False,
            "human_approval_required": True,
        }
    )


@app.post("/v1/mutations/stage")
def stage_mutation():
    body = request.get_json(silent=True) or {}
    relative_path = str(body.get("path") or "").strip()
    content = body.get("content")
    if not isinstance(content, str):
        return jsonify({"ok": False, "error": "content must be UTF-8 text"}), 400
    if len(content.encode("utf-8")) > MAX_CONTENT_BYTES:
        return jsonify({"ok": False, "error": "content exceeds candidate size limit"}), 413
    try:
        target = resolve_repo_path(relative_path)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    before_sha = current_sha(target)
    expected = body.get("expected_sha256")
    if expected is not None and str(expected) != str(before_sha):
        return jsonify({"ok": False, "error": "preimage SHA mismatch", "current_sha256": before_sha}), 409

    stage_id = secrets.token_hex(12)
    stage = MutationStage(
        stage_id=stage_id,
        approval_token=secrets.token_urlsafe(24),
        path=relative_path,
        expected_sha256=before_sha,
        proposed_sha256=sha256_bytes(content.encode("utf-8")),
        content=content,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _stages[stage_id] = stage
    result = stage.public()
    result["approval_token"] = stage.approval_token
    result["preview"] = content[:4000]
    result["preview_truncated"] = len(content) > 4000
    return jsonify({"ok": True, "mutation": result})


@app.get("/v1/mutations/<stage_id>")
def mutation_status(stage_id: str):
    stage = _stages.get(stage_id)
    if not stage:
        return jsonify({"ok": False, "error": "unknown stage"}), 404
    return jsonify({"ok": True, "mutation": stage.public()})


@app.post("/v1/mutations/<stage_id>/execute")
def execute_mutation(stage_id: str):
    stage = _stages.get(stage_id)
    if not stage:
        return jsonify({"ok": False, "error": "unknown stage"}), 404
    body = request.get_json(silent=True) or {}
    if body.get("confirm") != "APPROVE":
        return jsonify({"ok": False, "error": "explicit APPROVE confirmation required"}), 403
    if not secrets.compare_digest(str(body.get("approval_token") or ""), stage.approval_token):
        return jsonify({"ok": False, "error": "approval token mismatch"}), 403
    if stage.status != "STAGED_AWAITING_HUMAN_APPROVAL":
        return jsonify({"ok": False, "error": "stage is not executable", "status": stage.status}), 409

    target = resolve_repo_path(stage.path)
    observed_sha = current_sha(target)
    if observed_sha != stage.expected_sha256:
        stage.status = "BLOCKED_PREIMAGE_CHANGED"
        return jsonify(
            {
                "ok": False,
                "error": "preimage changed after staging",
                "expected_sha256": stage.expected_sha256,
                "observed_sha256": observed_sha,
            }
        ), 409

    checkpoint_dir = checkpoint(stage, target)
    atomic_write(target, stage.content)
    written_sha = current_sha(target)
    if written_sha != stage.proposed_sha256:
        stage.status = "FAILED_POSTWRITE_HASH"
        return jsonify({"ok": False, "error": "post-write hash mismatch", "written_sha256": written_sha}), 500

    stage.status = "EXECUTED_WITH_CHECKPOINT"
    return jsonify(
        {
            "ok": True,
            "status": stage.status,
            "path": stage.path,
            "preimage_sha256": stage.expected_sha256,
            "written_sha256": written_sha,
            "checkpoint": str(checkpoint_dir),
            "shell_execution": False,
            "human_approval_verified": True,
        }
    )


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
