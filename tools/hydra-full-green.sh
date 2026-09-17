#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_DIR="${HYDRA_REPO_DIR:-$HOME/hydra-shell-android}"
LOG_DIR="${HYDRA_LOG_DIR:-$HOME/.hydra/logs}"
PID_DIR="${HYDRA_PID_DIR:-$HOME/.hydra/run}"
MUTATION_PORT="${HYDRA_MUTATION_PORT:-8790}"
VNC_DISPLAY="${HYDRA_VNC_DISPLAY:-:1}"
VNC_GEOMETRY="${HYDRA_VNC_GEOMETRY:-1080x1600}"
VNC_DEPTH="${HYDRA_VNC_DEPTH:-24}"
VNC_DPI="${HYDRA_VNC_DPI:-180}"
FAST_MODEL="${HYDRA_FAST_MODEL:-qwen3:0.6b}"
DEEP_MODEL="${HYDRA_DEEP_MODEL:-qwen2.5:3b}"

VNC_DISPLAY_NUM="${VNC_DISPLAY#:}"
VNC_PORT="$((5900 + VNC_DISPLAY_NUM))"

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
need_pkg vncserver tigervnc

port_open() {
  python - "$1" <<'PY'
import socket,sys
port=int(sys.argv[1])
s=socket.socket(); s.settimeout(.5)
try:
    ok=s.connect_ex(("127.0.0.1",port))==0
finally:
    s.close()
raise SystemExit(0 if ok else 1)
PY
}

printf '\n[1/4] Gated mutation gateway\n'
if port_open "$MUTATION_PORT"; then
  printf 'Mutation gateway GREEN on 127.0.0.1:%s (existing instance preserved)\n' "$MUTATION_PORT"
elif [ -f "$REPO_DIR/backend/candidate_workflow.py" ]; then
  nohup env \
    PYTHONUNBUFFERED=1 \
    LUHM_MUTATION_PORT="$MUTATION_PORT" \
    LUHM_REPO_ROOT="$REPO_DIR" \
    LUHM_MUTATION_STATE="$HOME/.local/state/luhm-mutation" \
    python "$REPO_DIR/backend/candidate_workflow.py" \
    >"$LOG_DIR/mutation-gateway.log" 2>&1 &
  echo $! >"$PID_DIR/mutation-gateway.pid"
  for _ in $(seq 1 10); do
    port_open "$MUTATION_PORT" && break
    sleep 1
  done
  port_open "$MUTATION_PORT" || {
    printf 'Mutation gateway failed. See %s\n' "$LOG_DIR/mutation-gateway.log"
    exit 1
  }
  printf 'Mutation gateway GREEN on 127.0.0.1:%s\n' "$MUTATION_PORT"
else
  printf 'Mutation gateway missing: %s\n' "$REPO_DIR/backend/candidate_workflow.py"
  exit 1
fi

printf '\n[2/4] TigerVNC\n'
export DISPLAY="$VNC_DISPLAY"

if port_open "$VNC_PORT"; then
  printf 'VNC GREEN on %s / 127.0.0.1:%s (live listener preserved)\n' "$VNC_DISPLAY" "$VNC_PORT"
else
  vncserver -list -cleanstale >/dev/null 2>&1 || true
  vncserver "$VNC_DISPLAY" \
    -localhost yes \
    -geometry "$VNC_GEOMETRY" \
    -depth "$VNC_DEPTH" \
    -dpi "$VNC_DPI"

  for _ in $(seq 1 10); do
    port_open "$VNC_PORT" && break
    sleep 1
  done
  port_open "$VNC_PORT" || {
    printf 'VNC failed to open 127.0.0.1:%s. Check ~/.vnc logs.\n' "$VNC_PORT"
    exit 1
  }
  printf 'VNC GREEN on %s / 127.0.0.1:%s\n' "$VNC_DISPLAY" "$VNC_PORT"
fi

printf '\n[3/4] Ollama + Hydra\n'
export HYDRA_FAST_MODEL="$FAST_MODEL"
export HYDRA_DEEP_MODEL="$DEEP_MODEL"
export HYDRA_OLLAMA_MODEL="$FAST_MODEL"

if [ -f "$PID_DIR/hydra-gateway.pid" ]; then
  old_pid="$(cat "$PID_DIR/hydra-gateway.pid" 2>/dev/null || true)"
  if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
    kill "$old_pid" 2>/dev/null || true
    sleep 1
  fi
fi
if port_open 8787; then
  pkill -f 'python.*backend/server.py' 2>/dev/null || true
  sleep 1
fi

"$REPO_DIR/tools/hydra-ollama-up.sh"

if command -v ollama >/dev/null 2>&1; then
  for model in "$FAST_MODEL" "$DEEP_MODEL"; do
    if ! ollama list | awk 'NR>1 {print $1}' | grep -Fxq "$model"; then
      printf 'Pulling %s...\n' "$model"
      ollama pull "$model"
    fi
  done
fi

printf '\n[4/4] Full localhost audit\n'
curl -fsS http://127.0.0.1:8787/v1/system/status | python -m json.tool
curl -fsS "http://127.0.0.1:${MUTATION_PORT}/health" | python -m json.tool

printf '\nHYDRA PROFESSOR GREEN FULL GREEN\n'
printf 'Mutation   : 127.0.0.1:%s\n' "$MUTATION_PORT"
printf 'VNC        : %s / 127.0.0.1:%s\n' "$VNC_DISPLAY" "$VNC_PORT"
printf 'Hydra UI   : http://127.0.0.1:8787/ui/index.html\n'
printf 'Hydra API  : http://127.0.0.1:8787\n'
printf 'Ollama     : http://127.0.0.1:11434\n'
printf 'FAST       : %s\n' "$FAST_MODEL"
printf 'DEEP       : %s\n' "$DEEP_MODEL"
printf '\nThe mutation gateway is the only active repo write surface and still requires explicit human approval.\n'
