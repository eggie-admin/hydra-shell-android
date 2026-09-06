from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def require_rclone() -> str:
    path = shutil.which("rclone")
    if not path:
        raise RuntimeError("rclone is not installed or not on PATH")
    return path


def backup_files(job_id: str, files: list[Path]) -> list[dict]:
    rclone = require_rclone()
    remote = os.environ.get("RCLONE_REMOTE", "drive:")
    dest_root = os.environ.get("RCLONE_DEST", "").strip()
    if not dest_root:
        raise RuntimeError("RCLONE_DEST is not configured")

    results = []
    for src in files:
        if not src.is_file():
            continue
        remote_path = f"{remote}{dest_root.rstrip('/')}/{job_id}/{src.name}"
        cmd = [rclone, "copyto", str(src), remote_path, "--checksum"]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        results.append({"source": str(src), "remote": remote_path})
    return results
