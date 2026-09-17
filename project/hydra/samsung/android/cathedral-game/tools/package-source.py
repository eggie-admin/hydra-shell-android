#!/usr/bin/env python3
"""Build a deterministic LuHm Cathedral source archive from source-manifest.json."""

from __future__ import annotations

import fnmatch
import gzip
import io
import json
import os
import sys
import tarfile
from pathlib import Path


def die(message: str) -> "NoReturn":
    raise SystemExit(f"SOURCE_BUNDLE_RED: {message}")


def should_exclude(rel: str, patterns: list[str]) -> bool:
    rel = rel.replace(os.sep, "/")
    return any(fnmatch.fnmatch(rel, pattern) for pattern in patterns)


def iter_files(root: Path, include: list[str], exclude: list[str]):
    seen: set[str] = set()
    for item in include:
        path = root / item
        if not path.exists():
            die(f"bundle include missing: {item}")
        candidates = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        for file_path in candidates:
            rel = file_path.relative_to(root).as_posix()
            if rel in seen or should_exclude(rel, exclude):
                continue
            seen.add(rel)
            yield rel, file_path


def main() -> int:
    if len(sys.argv) != 3:
        die("usage: package-source.py ROOT OUTPUT_TAR_GZ")

    root = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    manifest = json.loads((root / "source/source-manifest.json").read_text(encoding="utf-8"))
    bundle = manifest.get("bundle", {})
    include = bundle.get("include", [])
    exclude = bundle.get("exclude_globs", [])
    files = list(iter_files(root, include, exclude))

    output.parent.mkdir(parents=True, exist_ok=True)
    raw_tar = io.BytesIO()
    with tarfile.open(fileobj=raw_tar, mode="w", format=tarfile.PAX_FORMAT) as tf:
        for rel, file_path in files:
            data = file_path.read_bytes()
            info = tarfile.TarInfo(name=f"luhmos-cathedral-source/{rel}")
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if os.access(file_path, os.X_OK) else 0o644
            tf.addfile(info, io.BytesIO(data))

    raw_tar.seek(0)
    with output.open("wb") as out_file:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out_file, mtime=0, compresslevel=9) as gz:
            gz.write(raw_tar.getvalue())

    print("LUHM_SOURCE_BUNDLE_GREEN")
    print(f"files={len(files)}")
    print(f"output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
