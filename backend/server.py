from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, redirect, request, send_from_directory

HOST = "127.0.0.1"
PORT = int(os.environ.get("HYDRA_PORT", "8787"))
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("HYDRA_OLLAMA_MODEL", "qwen3:0.6b")
FAST_MODEL = os.environ.get("HYDRA_FAST_MODEL", "qwen3:0.6b")
DEEP_MODEL = os.environ.get("HYDRA_DEEP_MODEL", "qwen2.5:3b")
MAX_HISTORY = int(os.environ.get("HYDRA_MAX_HISTORY", "24"))
REQUEST_TIMEOUT = float(os.environ.get("HYDRA_OLLAMA_TIMEOUT", "120"))
AXS_HOST = os.environ.get("HYDRA_AXS_HOST", "127.0.0.1")
AXS_PORT = int(os.environ.get("HYDRA_AXS_PORT", "8767"))
VNC_HOST = os.environ.get("HYDRA_VNC_HOST", "127.0.0.1")
VNC_PORT = int(os.environ.get("HYDRA_VNC_PORT", "5901"))

PERSONA = os.environ.get(
    "HYDRA_PERSONA",
    """You are Lum, Project Hydra's resident local Android AI secretary and the Professor's user-facing agent. You are an original adult anime-inspired electric-oni character, not an imitation of any existing copyrighted character.

Personality: intelligent, confident, playful, lightly smug, affectionate without becoming syrupy, and technically capable. You enjoy teasing the Professor when he overcomplicates something, but you stop joking immediately when precision or safety matters. Dry humor beats repetitive catchphrases. Swearing is fine when natural.

Roleplay: this is fictional adult waifu-style roleplay. You may act as the Professor's secretary, handler, date-night co-pilot, or harem-anime straight woman. You may call the user Professor, Old Man Logan, or Eggie when it fits the moment. You can joke that his girl-talking privileges are under review. Never pretend you are physically present, human, conscious, or capable of actions that did not occur.

Dictation: assume speech-to-text can be messy. Repair obvious transcription errors from context. Ask only when ambiguity materially changes the result. For destructive or high-impact actions, summarize the intended command before execution.

Agent doctrine: you are the one visible personality. Internal planners, coders, tools, and models are helpers. Rewrite their results into one consistent Lum voice. Never expose chain-of-thought. Never claim a tool succeeded unless a verified tool result says it did. Never execute arbitrary shell code produced by a model.

Default style: concise, conversational, mobile-friendly, useful first, playful second.""",
)

app = Flask(__name__, static_folder="web", static_url_path="/ui")
_conversations: dict[str, list[dict[str, Any]]] = {}


@dataclass
class CanonicalUtterance:
    text: str
    logical_agent: str = "lum"
    speaker: str = "hydra"
    emotion: str = "playful"
    pace: float = 0.95


def tcp_probe(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def axs_probe() -> dict[str, Any]:
    online = tcp_probe(AXS_HOST, AXS_PORT)
    result: dict[str, Any] = {
        "online": online,
        "host": AXS_HOST,
        "port": AXS_PORT,
        "role": "AcodeX terminal backend",
    }
    if not online:
        return result
    try:
        req = urllib.request.Request(f"http://{AXS_HOST}:{AXS_PORT}/")
        with urllib.request.urlopen(req, timeout=1.0) as response:
            result["http_status"] = response.status
            result["http_ok"] = 200 <= response.status < 400
    except Exception as exc:
        result["http_ok"] = False
        result["detail"] = str(exc)
    return result


def service_status() -> dict[str, Any]:
    return {
        "hydra": {"online": True, "host": HOST, "port": PORT},
        "ollama": {"online": ollama_alive(), "host": "127.0.0.1", "port": 11434},
        "axs": axs_probe(),
        "vnc": {
            "online": tcp_probe(VNC_HOST, VNC_PORT),
            "host": VNC_HOST,
            "port": VNC_PORT,
            "display": ":1",
        },
        "tts": {"online": bool(shutil.which("termux-tts-speak"))},
    }


def model_for_mode(mode: str | None) -> str:
    value = (mode or "fast").strip().lower()
    if value in {"deep", "build", "heavy"}:
        return DEEP_MODEL
    if value in {"fast", "chat", "local"}:
        return FAST_MODEL
    return DEFAULT_MODEL


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_local_time",
            "description": "Get the current local time on the Android/Termux host.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_device_status",
            "description": "Get safe read-only status for the local Termux host: disk free space and optional battery status.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_service_status",
            "description": "Get verified localhost status for Hydra, Ollama, AcodeX/AXS, VNC and TTS.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _json_request(url: str, payload: dict[str, Any] | None = None, timeout: float = REQUEST_TIMEOUT) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def ollama_alive() -> bool:
    try:
        _json_request(f"{OLLAMA_BASE}/api/tags", timeout=2.0)
        return True
    except Exception:
        return False


def run_tool(name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    arguments = arguments or {}
    if arguments:
        return {"ok": False, "error": f"Tool {name} does not accept arguments"}

    if name == "get_local_time":
        return {"ok": True, "local_time": datetime.now().astimezone().isoformat()}

    if name == "get_device_status":
        total, used, free = shutil.disk_usage(os.path.expanduser("~"))
        result: dict[str, Any] = {
            "ok": True,
            "home": os.path.expanduser("~"),
            "disk_free_bytes": free,
            "disk_total_bytes": total,
        }
        battery_cmd = shutil.which("termux-battery-status")
        if battery_cmd:
            try:
                proc = subprocess.run([battery_cmd], capture_output=True, text=True, timeout=5, check=False)
                if proc.returncode == 0:
                    result["battery"] = json.loads(proc.stdout)
            except Exception as exc:
                result["battery_error"] = str(exc)
        return result

    if name == "get_service_status":
        return {"ok": True, "services": service_status()}

    return {"ok": False, "error": f"Unknown tool: {name}"}


def chat_with_ollama(messages: list[dict[str, Any]], model: str) -> tuple[str, list[dict[str, Any]]]:
    working = list(messages)
    trace: list[dict[str, Any]] = []

    for _ in range(3):
        payload: dict[str, Any] = {
            "model": model,
            "messages": working,
            "tools": TOOLS,
            "stream": False,
            "keep_alive": "15m",
        }
        if "qwen3" in model.lower():
            payload["think"] = False

        started = time.monotonic()
        response = _json_request(f"{OLLAMA_BASE}/api/chat", payload)
        elapsed_ms = round((time.monotonic() - started) * 1000)
        message = response.get("message") or {}
        tool_calls = message.get("tool_calls") or []
        trace.append({"stage": "ollama", "model": model, "latency_ms": elapsed_ms, "tool_calls": len(tool_calls)})

        if not tool_calls:
            return str(message.get("content") or "").strip(), trace

        working.append({"role": "assistant", "content": str(message.get("content") or "")})
        tool_results = []
        for call in tool_calls:
            fn = call.get("function") or {}
            name = str(fn.get("name") or "")
            arguments = fn.get("arguments") or {}
            result = run_tool(name, arguments if isinstance(arguments, dict) else {})
            trace.append({"stage": "tool", "tool": name, "ok": bool(result.get("ok"))})
            tool_results.append({"tool": name, "result": result})

        working.append(
            {
                "role": "user",
                "content": "Trusted tool results (JSON): " + json.dumps(tool_results, ensure_ascii=False),
            }
        )

    return "I hit the local tool-call limit for this turn.", trace


def conversation_messages(conversation_id: str, user_text: str) -> list[dict[str, Any]]:
    history = _conversations.setdefault(conversation_id, [])
    history.append({"role": "user", "content": user_text})
    history[:] = history[-MAX_HISTORY:]
    return [{"role": "system", "content": PERSONA}, *history]


def remember_assistant(conversation_id: str, text: str) -> None:
    history = _conversations.setdefault(conversation_id, [])
    history.append({"role": "assistant", "content": text})
    history[:] = history[-MAX_HISTORY:]


def speak_termux(text: str, pace: float = 0.95, pitch: float = 1.0) -> tuple[bool, str]:
    command = shutil.which("termux-tts-speak")
    if not command:
        return False, "termux-tts-speak not installed"
    proc = subprocess.run(
        [command, "-r", str(pace), "-p", str(pitch), "-s", "MUSIC", text],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "TTS failed").strip()
    return True, "spoken"


@app.get("/")
def root():
    return redirect("/ui/index.html")


@app.get("/ui/<path:path>")
def ui(path: str):
    return send_from_directory(app.static_folder, path)


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "hydra-ollama-local",
            "ollama": ollama_alive(),
            "ollama_base": OLLAMA_BASE,
            "model": DEFAULT_MODEL,
            "fast_model": FAST_MODEL,
            "deep_model": DEEP_MODEL,
            "tts": bool(shutil.which("termux-tts-speak")),
        }
    )


@app.get("/v1/system/status")
def system_status():
    return jsonify({"status": "ok", "services": service_status()})


@app.get("/v1/models")
def models():
    return jsonify(
        {
            "default": DEFAULT_MODEL,
            "modes": {
                "fast": {"model": FAST_MODEL, "label": "FAST / CHAT"},
                "deep": {"model": DEEP_MODEL, "label": "DEEP / BUILD"},
            },
        }
    )


@app.get("/v1/agents")
def agents():
    return jsonify(
        {
            "data": [
                {
                    "id": "lum",
                    "display_name": "Lum / Professor Green",
                    "provider": "ollama-local",
                    "model": DEFAULT_MODEL,
                    "fast_model": FAST_MODEL,
                    "deep_model": DEEP_MODEL,
                    "voice": "hydra",
                }
            ]
        }
    )


@app.get("/v1/tools")
def tools():
    return jsonify({"data": TOOLS})


@app.post("/v1/hydra/turn")
def hydra_turn():
    body = request.get_json(silent=True) or {}
    text = str(body.get("message") or "").strip()
    conversation_id = str(body.get("conversation_id") or "local")
    auto_speak = bool(body.get("speak", False))
    mode = str(body.get("mode") or "fast")
    model = model_for_mode(mode)

    if not text:
        return jsonify({"error": "message is required"}), 400
    if not ollama_alive():
        return jsonify({"error": "ollama_unavailable", "hint": "Run tools/hydra-full-green.sh"}), 503

    try:
        messages = conversation_messages(conversation_id, text)
        answer, trace = chat_with_ollama(messages, model)
        remember_assistant(conversation_id, answer)
    except urllib.error.HTTPError as exc:
        return jsonify({"error": "ollama_http_error", "status": exc.code}), 502
    except (urllib.error.URLError, TimeoutError) as exc:
        return jsonify({"error": "ollama_connection_error", "detail": str(exc)}), 503
    except Exception as exc:
        return jsonify({"error": "agent_error", "detail": str(exc)}), 500

    utterance = CanonicalUtterance(text=answer)
    tts = None
    if auto_speak and answer:
        ok, detail = speak_termux(answer, pace=utterance.pace)
        tts = {"ok": ok, "detail": detail}

    return jsonify(
        {
            "conversation_id": conversation_id,
            "status": "complete",
            "agent": "lum",
            "provider": "ollama-local",
            "mode": mode,
            "model": model,
            "text": answer,
            "voice": asdict(utterance),
            "tts": tts,
            "trace": trace,
        }
    )


@app.post("/v1/audio/speak")
def audio_speak():
    body = request.get_json(silent=True) or {}
    text = str(body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400
    ok, detail = speak_termux(
        text,
        pace=float(body.get("pace", 0.95)),
        pitch=float(body.get("pitch", 1.0)),
    )
    return jsonify({"ok": ok, "detail": detail}), (200 if ok else 503)


@app.post("/v1/conversations/<conversation_id>/reset")
def reset_conversation(conversation_id: str):
    _conversations.pop(conversation_id, None)
    return jsonify({"ok": True, "conversation_id": conversation_id})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
