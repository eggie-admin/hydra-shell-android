#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_DIR="${HYDRA_REPO_DIR:-$HOME/hydra-shell-android}"
MODEL="${HYDRA_OLLAMA_MODEL:-qwen2.5:3b}"
PORT="${HYDRA_PORT:-8787}"
LOG_DIR="${HYDRA_LOG_DIR:-$HOME/.hydra/logs}"
PID_DIR="${HYDRA_PID_DIR:-$HOME/.hydra/run}"
mkdir -p "$LOG_DIR" "$PID_DIR"

need_pkg() {
  local cmd="$1" pkg="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    pkg install -y "$pkg"
  fi
}

need_pkg python python
need_pkg curl curl
need_pkg git git

if ! command -v ollama >/dev/null 2>&1; then
  printf 'Ollama is not installed in this Termux environment.\n'
  printf 'Install your working Ollama package/build first, then rerun this script.\n'
  exit 1
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/eggie-admin/hydra-shell-android.git "$REPO_DIR"
fi

cd "$REPO_DIR"

if git show-ref --verify --quiet refs/remotes/origin/hydra-ollama-local-001; then
  git checkout hydra-ollama-local-001 2>/dev/null || git checkout -b hydra-ollama-local-001 origin/hydra-ollama-local-001
  git pull --ff-only origin hydra-ollama-local-001 || true
fi

python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  printf 'Starting Ollama...\n'
  nohup ollama serve >"$LOG_DIR/ollama.log" 2>&1 &
  echo $! >"$PID_DIR/ollama.pid"
  for _ in $(seq 1 30); do
    curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  printf 'Ollama did not become ready. See %s\n' "$LOG_DIR/ollama.log"
  exit 1
fi

if ! ollama list | awk 'NR>1 {print $1}' | grep -Fxq "$MODEL"; then
  printf 'Pulling model %s...\n' "$MODEL"
  ollama pull "$MODEL"
fi

export HYDRA_OLLAMA_MODEL="$MODEL"
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
export HYDRA_PORT="$PORT"

if curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
  printf 'Hydra gateway already running on %s.\n' "$PORT"
else
  printf 'Starting Hydra gateway...\n'
  nohup python backend/server.py >"$LOG_DIR/hydra-gateway.log" 2>&1 &
  echo $! >"$PID_DIR/hydra-gateway.pid"
  for _ in $(seq 1 20); do
    curl -fsS "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 && break
    sleep 1
  done
fi

printf '\nHYDRA LOCAL GREEN\n'
printf 'UI:     http://127.0.0.1:%s/ui/index.html\n' "$PORT"
printf 'Health: http://127.0.0.1:%s/health\n' "$PORT"
printf 'Model:  %s\n' "$MODEL"
printf 'Logs:   %s\n' "$LOG_DIR"
printf '\nQuick test:\n'
printf "curl -s -H 'Content-Type: application/json' -d '{\"message\":\"Say hello and tell me your local model.\"}' http://127.0.0.1:%s/v1/hydra/turn\n" "$PORT"
