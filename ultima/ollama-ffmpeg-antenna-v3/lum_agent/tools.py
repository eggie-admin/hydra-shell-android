from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from agents.decorators import tool

from .doctrine import list_skills, load_skill

RUNTIME_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CODE_ROOT = RUNTIME_DIR.parents[1]
CODE_ROOT = Path(os.environ.get("KAI_CODE_ROOT", str(DEFAULT_CODE_ROOT))).resolve()
DENY_PARTS = {".git", ".secrets", "secrets", "keys", "node_modules", "__pycache__", ".venv", "venv"}
ALLOWED_READ_SUFFIXES = {".py", ".pyi", ".md", ".json", ".toml", ".yml", ".yaml", ".js", ".html", ".css", ".java", ".sh"}
SECRET_PATTERN = re.compile(
    r"(?:\bsk-[A-Za-z0-9_-]{20,}\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAIza[0-9A-Za-z_-]{30,}\b)"
)


def _safe_path(value: str, *, python_only: bool = False) -> Path:
    raw = Path(value.strip())
    if not value.strip() or raw.is_absolute():
        raise ValueError("Path must be repository-relative")
    if any(part in DENY_PARTS or part.startswith(".env") for part in raw.parts):
        raise ValueError("Path is denied by policy")
    path = (CODE_ROOT / raw).resolve()
    path.relative_to(CODE_ROOT)
    if not path.is_file():
        raise FileNotFoundError(value)
    if python_only and path.suffix.lower() not in {".py", ".pyi"}:
        raise ValueError("Python tool requires a .py or .pyi file")
    if path.suffix.lower() not in ALLOWED_READ_SUFFIXES:
        raise ValueError("File type is not allow-listed")
    if path.stat().st_size > 262_144:
        raise ValueError("File exceeds 256 KiB read limit")
    return path


def _relative(path: Path) -> str:
    return path.relative_to(CODE_ROOT).as_posix()


def _source(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if SECRET_PATTERN.search(text):
        raise ValueError("Secret-shaped content detected; file is not eligible for agent inspection")
    return text


@tool
def list_lum_skills() -> str:
    """List the doctrine skills Lum can load for the current task."""
    return json.dumps(list_skills(), indent=2)


@tool
def load_lum_skill(name: str) -> str:
    """Load one named Lum doctrine skill. Use only when it materially applies."""
    return load_skill(name)


@tool
def read_source(path: str, max_chars: int = 12000) -> str:
    """Read one allow-listed repository source file without executing it."""
    target = _safe_path(path)
    limit = min(max(max_chars, 500), 20000)
    text = _source(target)
    return json.dumps(
        {
            "path": _relative(target),
            "chars": len(text),
            "truncated": len(text) > limit,
            "content": text[:limit],
        },
        ensure_ascii=False,
    )


@tool
def search_source(query: str, suffix: str = ".py", limit: int = 20) -> str:
    """Search allow-listed repository text. Defaults to Python source only."""
    needle = query.strip()
    if not needle or len(needle) > 160:
        raise ValueError("Query must be 1-160 characters")
    suffix = suffix.strip().lower()
    if suffix and suffix not in ALLOWED_READ_SUFFIXES:
        raise ValueError("Suffix is not allow-listed")
    max_hits = min(max(limit, 1), 50)
    hits: list[dict[str, Any]] = []
    for path in CODE_ROOT.rglob(f"*{suffix}" if suffix else "*"):
        if len(hits) >= max_hits:
            break
        if not path.is_file() or path.is_symlink():
            continue
        try:
            rel = path.resolve().relative_to(CODE_ROOT)
        except (OSError, ValueError):
            continue
        if any(part in DENY_PARTS or part.startswith(".env") for part in rel.parts):
            continue
        if path.suffix.lower() not in ALLOWED_READ_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if SECRET_PATTERN.search(text):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if needle.casefold() in line.casefold():
                hits.append({"path": rel.as_posix(), "line": lineno, "text": line[:300]})
                if len(hits) >= max_hits:
                    break
    return json.dumps({"query": needle, "suffix": suffix, "hits": hits}, ensure_ascii=False)


@tool
def python_outline(path: str) -> str:
    """Parse Python with ast and return imports, constants, classes, functions, and async functions."""
    target = _safe_path(path, python_only=True)
    tree = ast.parse(_source(target), filename=str(target))
    result: dict[str, Any] = {
        "path": _relative(target),
        "imports": [],
        "constants": [],
        "classes": [],
        "functions": [],
        "async_functions": [],
    }
    for node in tree.body:
        if isinstance(node, ast.Import):
            result["imports"].extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level + (node.module or "")
            result["imports"].append(prefix)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            names: list[str] = []
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for item in targets:
                if isinstance(item, ast.Name) and item.id.isupper():
                    names.append(item.id)
            result["constants"].extend(names)
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.AsyncFunctionDef):
            result["async_functions"].append({"name": node.name, "line": node.lineno})
    return json.dumps(result, indent=2)


@tool
def python_compile(path: str) -> str:
    """Compile one Python file with CPython without importing or running application code."""
    target = _safe_path(path, python_only=True)
    if target.suffix.lower() != ".py":
        raise ValueError("py_compile requires a .py file")
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", str(target)],
        cwd=str(CODE_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return json.dumps(
        {
            "path": _relative(target),
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stderr": proc.stderr[-4000:],
            "evidence": "py_compile only; no runtime/integration claim",
        }
    )


@tool
def propose_spell(spell: str, args_json: str = "{}") -> str:
    """Describe an existing KAI spell proposal without executing or approving it."""
    from magic_chat import SPELLS

    name = spell.strip().upper()
    spec = SPELLS.get(name)
    if spec is None:
        raise ValueError("Unknown spell")
    args = json.loads(args_json or "{}")
    if not isinstance(args, dict):
        raise ValueError("args_json must decode to an object")
    return json.dumps(
        {
            "spell": name,
            "args": args,
            "spec": spec,
            "execution": "NOT_EXECUTED",
            "human_approval_required": bool(spec.get("approval")),
            "next_endpoint": "/api/magic/cast/prepare",
        },
        indent=2,
    )


LUM_TOOLS = [
    list_lum_skills,
    load_lum_skill,
    read_source,
    search_source,
    python_outline,
    python_compile,
    propose_spell,
]
