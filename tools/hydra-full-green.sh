#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

REPO_DIR="${HYDRA_REPO_DIR:-$HOME/hydra-shell-android}"
LOG_DIR="${HYDRA_LOG_DIR:-$HOME/.hydra/logs}"
PID_DIR="${HYDRA_PID_DIR:-$HOME/.hydra/run}"
AXS_PORT="${HYDRA_AXS_PORT:-8767}"
VNC_DISPLAY="${HYDRA_VNC_DISPLAY:-:1}"
VNC_GEOMETRY="${HYDRA_VNC_GEOMETRY:-1080x1600}"
VNC_DEPTH="${HYDRA_VNC_DEPTH:-24}"
VNC_DPI="${HYDRA_VNC_DPI:-180}"
FAST_MODEL="${HYDRA_FAST_MODEL:-qwen3:0.6b}"
DEEP_MODEL="${HYDRA_DEEP_MODEL:-qwen2.5:3b}"

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

printf '\n[1/4] AcodeX / AXS\n'
if port_open "$AXS_PORT"; then
  printf 'AXS GREEN on 127.0.0.1:%s (existing instance preserved)\n' "$AXS_PORT"
elif command -v axs >/dev/null 2>&1; then
  nohup axs >"$LOG_DIR/axs.log" 2>&1 &
  echo $! >"$PID_DIR/axs.pid"
  for _ in $(seq 1 10); do
    port_open "$AXS_PORT" && break
    sleep 1
  done
  port_open "$AXS_PORT" || { printf 'AXS failed. See %s\n' "$LOG_DIR/axs.log"; exit 1; }
  printf 'AXS GREEN on 127.0.0.1:%s\n' "$AXS_PORT"
elif command -v acodeX-server >/dev/null 2>&1; then
  nohup acodeX-server >"$LOG_DIR/axs.log" 2>&1 &
  echo $! >"$PID_DIR/axs.pid"
  for _ in $(seq 1 10); do
    port_open "$AXS_PORT" && break
    sleep 1
  done
  port_open "$AXS_PORT" || { printf 'AcodeX server failed. See %s\n' "$LOG_DIR/axs.log"; exit 1; }
  printf 'AXS GREEN on 127.0.0.1:%s\n' "$AXS_PORT"
else
  printf 'AXS YELLOW: no axs/acodeX-server command found. Existing AcodeX-managed server may still be used.\n'
fi

printf '\n[2/4] TigerVNC\n'
export DISPLAY="$VNC_DISPLAY"
if vncserver -list 2>/dev/null | grep -q "${VNC_DISPLAY}"; then
  printf 'VNC GREEN on %s (existing session preserved)\n' "$VNC_DISPLAY"
else
  vncserver -list -cleanstale >/dev/null 2>&1 || true
  vncserver "$VNC_DISPLAY" \
    -localhost yes \
    -geometry "$VNC_GEOMETRY" \
    -depth "$VNC_DEPTH" \
    -dpi "$VNC_DPI"
  printf 'VNC GREEN on %s / 127.0.0.1:5901\n' "$VNC_DISPLAY"
fi

printf '\n[3/4] Ollama + Hydra\n'
export HYDRA_FAST_MODEL="$FAST_MODEL"
export HYDRA_DEEP_MODEL="$DEEP_MODEL"
export HYDRA_OLLAMA_MODEL="$FAST_MODEL"
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

printf '\nHYDRA PROFESSOR GREEN FULL GREEN\n'
printf 'AcodeX/AXS : 127.0.0.1:%s\n' "$AXS_PORT"
printf 'VNC        : %s / 127.0.0.1:5901\n' "$VNC_DISPLAY"
printf 'Hydra UI   : http://127.0.0.1:8787/ui/index.html\n'
printf 'Hydra API  : http://127.0.0.1:8787\n'
printf 'Ollama     : http://127.0.0.1:11434\n'
printf 'FAST       : %s\n' "$FAST_MODEL"
printf 'DEEP       : %s\n' "$DEEP_MODEL"
printf '\nIn AcodeX terminal settings use host 127.0.0.1 and port %s.\n' "$AXS_PORT"
