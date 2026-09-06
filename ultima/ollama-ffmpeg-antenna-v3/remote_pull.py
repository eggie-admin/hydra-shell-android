from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Fast-forward-only GitHub remote pull for the Ultima antenna.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--branch", default="feature/ultima-ollama-ffmpeg-antenna-v3")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a git checkout: {repo}")

    run(["git", "status", "--short"], repo)
    run(["git", "fetch", "--prune", args.remote, args.branch], repo)
    run(["git", "pull", "--ff-only", args.remote, args.branch], repo)
    print("REMOTE PULL GREEN")


if __name__ == "__main__":
    main()
