from __future__ import annotations

import hashlib
import html
import json
import os
import secrets
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, make_response, request, send_from_directory

HOST = "127.0.0.1"
PORT = int(os.environ.get("LUHM_MUTATION_PORT", "8790"))
REPO_ROOT = Path(os.environ.get("LUHM_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()
STATE_ROOT = Path(os.environ.get("LUHM_MUTATION_STATE", Path.home() / ".local/state/luhm-mutation")).expanduser().resolve()
WEB_ROOT = Path(__file__).resolve().parent / "web"
MAX_CONTENT_BYTES = int(os.environ.get("LUHM_MUTATION_MAX_BYTES", str(1024 * 1024)))
DENIED_PARTS = {".git", ".secrets", "secrets", "secret", "credentials", "private_keys"}
DENIED_NAMES = {".env", "id_rsa", "id_ed25519", "authorized_keys"}
PROOF_SCHEMA = "luhm-os.mutation-proof.v1"
PROOF_CSP = "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"

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


def canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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


def proof_root() -> Path:
    root = STATE_ROOT / "proofs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def proof_paths(stage_id: str) -> tuple[Path, Path]:
    root = proof_root()
    return root / f"{stage_id}.json", root / f"{stage_id}.html"


def chat_proof_summary(payload: dict[str, Any], payload_sha256: str) -> str:
    return "\n".join(
        [
            "LUHM_MUTATION_PROOF_V1",
            f"stage_id={payload['stage_id']}",
            f"path={payload['path']}",
            f"preimage_sha256={payload['preimage_sha256'] or '(new file)'}",
            f"written_sha256={payload['written_sha256']}",
            f"payload_sha256={payload_sha256}",
            "human_approval_verified=true",
            "shell_execution=false",
            "authority_grant=none",
        ]
    )


def render_proof_html(proof: dict[str, Any]) -> str:
    payload = proof["payload"]
    safe_payload = html.escape(json.dumps(payload, indent=2, ensure_ascii=False))
    safe_chat = html.escape(proof["chat_summary"])
    safe_digest = html.escape(proof["payload_sha256"])
    safe_stage = html.escape(str(payload["stage_id"]))
    safe_path = html.escape(str(payload["path"]))
    safe_written = html.escape(str(payload["written_sha256"]))
    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<meta http-equiv=\"Content-Security-Policy\" content=\"{PROOF_CSP}\">
<meta name=\"referrer\" content=\"no-referrer\">
<title>LuHm Mutation Proof {safe_stage}</title>
<style>
:root{{color-scheme:dark;--bg:#060908;--panel:#0c1412;--ink:#effff9;--mint:#6bf1c8;--dim:#97aaa4;--line:#23443a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}}main{{max-width:900px;margin:auto;padding:24px}}section{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin:12px 0}}h1{{font-size:1.4rem}}h2{{font-size:1rem;color:var(--mint)}}code,pre{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}pre{{white-space:pre-wrap;word-break:break-word;background:#050807;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto}}.ok{{color:var(--mint)}}.dim{{color:var(--dim)}}dl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 12px}}dt{{color:var(--dim)}}dd{{margin:0;word-break:break-all}}
</style>
</head>
<body><main>
<h1>LuHm bounded mutation proof</h1>
<p class=\"ok\">EXECUTED WITH HUMAN APPROVAL + CHECKPOINT</p>
<section><h2>Identity</h2><dl>
<dt>Schema</dt><dd>{PROOF_SCHEMA}</dd>
<dt>Stage</dt><dd>{safe_stage}</dd>
<dt>Path</dt><dd>{safe_path}</dd>
<dt>Written SHA-256</dt><dd>{safe_written}</dd>
<dt>Payload SHA-256</dt><dd>{safe_digest}</dd>
</dl></section>
<section><h2>Chat proof</h2><p class=\"dim\">Safe to paste into chat. It contains no approval token and no file content.</p><pre>{safe_chat}</pre></section>
<section><h2>Canonical proof payload</h2><pre>{safe_payload}</pre></section>
<section><h2>Authority boundary</h2><p>This receipt proves one bounded UTF-8 file mutation. It grants no merge, signing, install, deploy, release, shell, DNS, billing, or publication authority.</p></section>
</main></body></html>\n"""


def write_proof(stage: MutationStage, written_sha: str, checkpoint_dir: Path) -> dict[str, Any]:
    executed_at = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        "schema": PROOF_SCHEMA,
        "stage_id": stage.stage_id,
        "mutation_status": "EXECUTED_WITH_CHECKPOINT",
        "path": stage.path,
        "created_at": stage.created_at,
        "executed_at": executed_at,
        "preimage_sha256": stage.expected_sha256,
        "proposed_sha256": stage.proposed_sha256,
        "written_sha256": written_sha,
        "checkpoint_id": checkpoint_dir.name,
        "human_approval_verified": True,
        "shell_execution": False,
        "file_content_included": False,
        "approval_token_included": False,
        "authority_grant": "NONE",
    }
    payload_sha256 = sha256_bytes(canonical_json_bytes(payload))
    proof = {
        "payload": payload,
        "payload_sha256": payload_sha256,
        "chat_summary": chat_proof_summary(payload, payload_sha256),
    }
    json_path, html_path = proof_paths(stage.stage_id)
    json_path.write_text(json.dumps(proof, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    html_path.write_text(render_proof_html(proof), encoding="utf-8")
    return {
        "schema": PROOF_SCHEMA,
        "payload_sha256": payload_sha256,
        "json_url": f"/v1/mutations/{stage.stage_id}/proof.json",
        "html_url": f"/v1/mutations/{stage.stage_id}/proof.html",
        "chat_summary": proof["chat_summary"],
    }


def proof_response(stage_id: str, kind: str):
    json_path, html_path = proof_paths(stage_id)
    path = json_path if kind == "json" else html_path
    if not path.exists():
        return jsonify({"ok": False, "error": "proof not available; mutation must execute successfully first"}), 404
    response = make_response(path.read_text(encoding="utf-8"))
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if kind == "json":
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        response.headers["Content-Disposition"] = f'attachment; filename="luhm-mutation-proof-{stage_id}.json"'
    else:
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Content-Security-Policy"] = PROOF_CSP
        response.headers["Referrer-Policy"] = "no-referrer"
    return response


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
            "proof_schema": PROOF_SCHEMA,
            "proof_renderers": ["json", "html", "chat_summary"],
            "proof_contains_file_content": False,
            "proof_contains_approval_token": False,
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


@app.get("/v1/mutations/<stage_id>/proof.json")
def mutation_proof_json(stage_id: str):
    return proof_response(stage_id, "json")


@app.get("/v1/mutations/<stage_id>/proof.html")
def mutation_proof_html(stage_id: str):
    return proof_response(stage_id, "html")


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
    proof = write_proof(stage, written_sha, checkpoint_dir)
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
            "proof": proof,
        }
    )


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
