#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
GAME="$(cd "$HERE/.." && pwd)"
export PYTHONPATH="$GAME/python/src${PYTHONPATH:+:$PYTHONPATH}"
python - <<'PY'
import importlib.util
missing=[name for name in ("fastapi","uvicorn") if importlib.util.find_spec(name) is None]
if missing:
    raise SystemExit("LUHM_HARNESS_DEPENDENCY_MISSING: install the project Python dependencies first: "+",".join(missing))
print("LUHM_LOCAL_HARNESS_DEPENDENCIES_GREEN")
PY
export LUHM_PAIR_CODE="$(python - <<'PY'
import secrets
print(f"{secrets.randbelow(1_000_000):06d}")
PY
)"
printf '\nLUHM LOCAL HARNESS\nPAIR CODE: %s\nPORT: 8791\nCTRL-C TO STOP\n\n' "$LUHM_PAIR_CODE"
exec python -m uvicorn luhm_core.local_harness:app --host 127.0.0.1 --port 8791 --no-access-log
