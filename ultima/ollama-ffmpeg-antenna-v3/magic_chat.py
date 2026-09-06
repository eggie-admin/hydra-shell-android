from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

ROUTER = APIRouter(prefix="/api/magic", tags=["magic"])
RUNTIME_DIR = Path(__file__).resolve().parent
DEFAULT_CODE_ROOT = RUNTIME_DIR.parents[1]
CODE_ROOT = Path(os.environ.get("KAI_CODE_ROOT", str(DEFAULT_CODE_ROOT))).resolve()
STATE_ROOT = Path(os.environ.get("KAI_MAGIC_STATE", str(RUNTIME_DIR / "data" / "magic"))).resolve()
CHECKPOINT_ROOT = STATE_ROOT / "checkpoints"
CHECKPOINT_ROOT.mkdir(parents=True, exist_ok=True)
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/responses")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-6-astra")

ALLOWED_SUFFIXES = {
    ".py", ".js", ".html", ".css", ".json", ".toml", ".md", ".txt", ".yml", ".yaml", ".sh"
}
DENY_PARTS = {".git", ".secrets", "secrets", "keys", "node_modules", "__pycache__"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "cloudflare_account_token": re.compile(r"\bcfat_[A-Za-z0-9_-]{20,}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}

SPELLS: dict[str, dict[str, Any]] = {
    "INSPECT": {"school": "white", "rank": 0, "mp": 1, "approval": False, "mutates": False},
    "READ_FILE": {"school": "white", "rank": 0, "mp": 1, "approval": False, "mutates": False},
    "SEARCH_TEXT": {"school": "blue", "rank": 0, "mp": 2, "approval": False, "mutates": False},
    "PYTHON_CHECK": {"school": "green", "rank": 1, "mp": 4, "approval": False, "mutates": False},
    "GIT_DIFF": {"school": "time", "rank": 1, "mp": 3, "approval": False, "mutates": False},
    "WRITE_FILE": {"school": "black", "rank": 2, "mp": 5, "approval": True, "mutates": True},
    "ULTIMA": {"school": "ultima", "rank": 4, "mp": 99, "approval": True, "mutates": True, "disabled": True},
}

PENDING: dict[str, dict[str, Any]] = {}
CAST_TTL_SECONDS = 180


class MagicChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    model: str | None = None


class PrepareCastRequest(BaseModel):
    spell: str
    args: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    approved: bool


class RollbackRequest(BaseModel):
    approved: bool = False


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_path(value: str, *, must_exist: bool | None = None) -> Path:
    if not value or Path(value).is_absolute():
        raise HTTPException(status_code=400, detail="Path must be repository-relative")
    raw = Path(value)
    if any(part in DENY_PARTS or part.startswith(".env") for part in raw.parts):
        raise HTTPException(status_code=403, detail="Path is denied by policy")
    target = (CODE_ROOT / raw).resolve()
    try:
        target.relative_to(CODE_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="Path escapes code root") from exc
    if target.suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=403, detail="File type is not allow-listed")
    if must_exist is True and not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if must_exist is False and target.exists():
        raise HTTPException(status_code=409, detail="Target already exists")
    return target


def _iter_source_files() -> Iterator[Path]:
    for path in CODE_ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            resolved = path.resolve()
            rel = resolved.relative_to(CODE_ROOT)
        except (OSError, ValueError):
            continue
        if any(part in DENY_PARTS or part.startswith(".env") for part in rel.parts):
            continue
        if resolved.suffix.lower() in ALLOWED_SUFFIXES:
            yield resolved


def _reject_secrets(text: str) -> None:
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            raise HTTPException(status_code=400, detail=f"Secret-shaped content rejected: {label}")


def _clean_pending() -> None:
    now = time.time()
    expired = [cast_id for cast_id, item in PENDING.items() if now - item["created"] > CAST_TTL_SECONDS]
    for cast_id in expired:
        PENDING.pop(cast_id, None)


def _extract_openai_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    parts: list[str] = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts).strip()


def _openai_instructions() -> str:
    names = ", ".join(SPELLS)
    return (
        "You are the KAI 9000 in-app coding planner. Be concise and operational. "
        "Never claim a tool or spell executed unless the application returns execution evidence. "
        "Prefer inspect/read/search before mutation. Never request secrets. Never place credentials in source. "
        "When suggesting an app action, reference only these spell names: " + names + ". "
        "WRITE_FILE always requires human approval and optimistic SHA checking. "
        "ULTIMA is human-only and disabled in this runtime. Do not reveal private chain-of-thought."
    )


def _execute(spell: str, args: dict[str, Any], cast_id: str) -> dict[str, Any]:
    if spell == "ULTIMA":
        raise HTTPException(status_code=403, detail="ULTIMA is disabled in the in-app runtime")

    if spell == "INSPECT":
        limit = min(max(int(args.get("limit", 120)), 1), 300)
        files: list[str] = []
        for path in _iter_source_files():
            files.append(path.relative_to(CODE_ROOT).as_posix())
            if len(files) >= limit:
                break
        return {"ok": True, "spell": spell, "files": files, "truncated": len(files) >= limit}

    if spell == "READ_FILE":
        path = _safe_path(str(args.get("path", "")), must_exist=True)
        if path.stat().st_size > 262_144:
            raise HTTPException(status_code=413, detail="File exceeds 256 KiB read limit")
        return {
            "ok": True,
            "spell": spell,
            "path": path.relative_to(CODE_ROOT).as_posix(),
            "sha256": _sha256_bytes(path.read_bytes()),
            "content": path.read_text(encoding="utf-8"),
        }

    if spell == "SEARCH_TEXT":
        query = str(args.get("query", "")).strip()
        if not query or len(query) > 160:
            raise HTTPException(status_code=400, detail="Search query must be 1-160 characters")
        hits: list[dict[str, Any]] = []
        for path in _iter_source_files():
            if len(hits) >= 50:
                break
            try:
                for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if query.lower() in line.lower():
                        hits.append({"path": path.relative_to(CODE_ROOT).as_posix(), "line": lineno, "text": line[:300]})
                        if len(hits) >= 50:
                            break
            except (UnicodeDecodeError, OSError):
                continue
        return {"ok": True, "spell": spell, "query": query, "hits": hits}

    if spell == "PYTHON_CHECK":
        path = _safe_path(str(args.get("path", "")), must_exist=True)
        if path.suffix.lower() != ".py":
            raise HTTPException(status_code=400, detail="PYTHON_CHECK only accepts .py files")
        proc = subprocess.run(
            ["python3", "-m", "py_compile", str(path)],
            cwd=str(CODE_ROOT), capture_output=True, text=True, timeout=30, check=False,
        )
        return {"ok": proc.returncode == 0, "spell": spell, "returncode": proc.returncode, "stderr": proc.stderr[-4000:]}

    if spell == "GIT_DIFF":
        rel = str(args.get("path", "")).strip()
        cmd = ["git", "-C", str(CODE_ROOT), "diff", "--no-ext-diff", "--"]
        if rel:
            path = _safe_path(rel, must_exist=None)
            cmd.append(path.relative_to(CODE_ROOT).as_posix())
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
        return {"ok": proc.returncode == 0, "spell": spell, "returncode": proc.returncode, "diff": proc.stdout[-12000:], "stderr": proc.stderr[-2000:]}

    if spell == "WRITE_FILE":
        rel = str(args.get("path", ""))
        content = str(args.get("content", ""))
        if len(content.encode("utf-8")) > 262_144:
            raise HTTPException(status_code=413, detail="WRITE_FILE exceeds 256 KiB limit")
        _reject_secrets(content)
        path = _safe_path(rel, must_exist=None)
        existed = path.is_file()
        before = path.read_bytes() if existed else b""
        expected = args.get("old_sha256")
        actual = _sha256_bytes(before) if existed else None
        if existed and expected != actual:
            raise HTTPException(status_code=409, detail={"message": "Stale write rejected", "expected_old_sha256": actual})
        if not existed and expected not in {None, ""}:
            raise HTTPException(status_code=409, detail="old_sha256 must be empty for a new file")

        checkpoint_dir = CHECKPOINT_ROOT / cast_id
        checkpoint_dir.mkdir(parents=True, exist_ok=False)
        checkpoint_path = checkpoint_dir / "checkpoint.json"
        checkpoint = {
            "cast_id": cast_id,
            "path": path.relative_to(CODE_ROOT).as_posix(),
            "existed": existed,
            "before_sha256": actual,
            "before_base64": base64.b64encode(before).decode("ascii"),
            "created_unix": int(time.time()),
        }
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        after = _sha256_bytes(path.read_bytes())
        checkpoint["after_sha256"] = after
        checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
        return {
            "ok": True,
            "spell": spell,
            "path": checkpoint["path"],
            "before_sha256": actual,
            "after_sha256": after,
            "checkpoint": cast_id,
        }

    raise HTTPException(status_code=400, detail="Unknown spell")


@ROUTER.get("/spells")
def list_spells() -> dict[str, Any]:
    return {"ok": True, "code_root": str(CODE_ROOT), "spells": SPELLS}


@ROUTER.post("/chat")
def magic_chat(req: MagicChatRequest) -> dict[str, Any]:
    _reject_secrets(req.message)
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return {
            "ok": True,
            "mode": "deterministic_mock",
            "model": None,
            "assistant": "OpenAI is not configured. Inspect with INSPECT/READ_FILE/SEARCH_TEXT, validate with PYTHON_CHECK/GIT_DIFF, and require approval before WRITE_FILE.",
        }
    payload = {
        "model": req.model or OPENAI_MODEL,
        "instructions": _openai_instructions(),
        "input": req.message,
        "store": False,
        "max_output_tokens": 1600,
    }
    try:
        response = httpx.post(
            OPENAI_API_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}") from exc
    return {
        "ok": True,
        "mode": "openai",
        "model": req.model or OPENAI_MODEL,
        "assistant": _extract_openai_text(data),
        "response_id": data.get("id"),
    }


@ROUTER.post("/cast/prepare")
def prepare_cast(req: PrepareCastRequest) -> dict[str, Any]:
    _clean_pending()
    spell = req.spell.strip().upper()
    spec = SPELLS.get(spell)
    if not spec:
        raise HTTPException(status_code=400, detail="Unknown spell")
    cast_id = uuid.uuid4().hex
    PENDING[cast_id] = {
        "spell": spell,
        "args": req.args,
        "approved": not spec["approval"],
        "created": time.time(),
        "executed": False,
    }
    return {
        "ok": True,
        "cast_id": cast_id,
        "spell": spell,
        "spec": spec,
        "approved": PENDING[cast_id]["approved"],
        "expires_in": CAST_TTL_SECONDS,
    }


@ROUTER.post("/cast/{cast_id}/approve")
def approve_cast(cast_id: str, req: ApprovalRequest) -> dict[str, Any]:
    _clean_pending()
    item = PENDING.get(cast_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cast not found or expired")
    if item["executed"]:
        raise HTTPException(status_code=409, detail="Cast already executed")
    item["approved"] = bool(req.approved)
    return {"ok": True, "cast_id": cast_id, "approved": item["approved"]}


@ROUTER.post("/cast/{cast_id}/execute")
def execute_cast(cast_id: str) -> dict[str, Any]:
    _clean_pending()
    item = PENDING.get(cast_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cast not found or expired")
    if item["executed"]:
        raise HTTPException(status_code=409, detail="Cast already executed")
    if not item["approved"]:
        raise HTTPException(status_code=409, detail="Human approval required")
    result = _execute(item["spell"], item["args"], cast_id)
    item["executed"] = True
    item["result"] = result
    return {"ok": True, "cast_id": cast_id, "result": result}


@ROUTER.post("/cast/{cast_id}/rollback")
def rollback_cast(cast_id: str, req: RollbackRequest) -> dict[str, Any]:
    if not req.approved:
        raise HTTPException(status_code=409, detail="Human approval required for rollback")
    checkpoint_path = CHECKPOINT_ROOT / cast_id / "checkpoint.json"
    if not checkpoint_path.is_file():
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    expected_after = checkpoint.get("after_sha256")
    if not expected_after:
        raise HTTPException(status_code=409, detail="Checkpoint lacks an after-SHA and cannot be rolled back safely")
    path = _safe_path(checkpoint["path"], must_exist=None)
    current_sha = _sha256_bytes(path.read_bytes()) if path.is_file() else None
    if current_sha != expected_after:
        raise HTTPException(
            status_code=409,
            detail={"message": "Rollback conflict: file changed after cast", "expected_current_sha256": expected_after, "actual_current_sha256": current_sha},
        )
    before = base64.b64decode(checkpoint["before_base64"])
    if checkpoint["existed"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(before)
    else:
        path.unlink(missing_ok=True)
    return {
        "ok": True,
        "cast_id": cast_id,
        "rolled_back": checkpoint["path"],
        "restored_sha256": checkpoint["before_sha256"],
    }
