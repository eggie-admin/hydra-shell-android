#!/usr/bin/env python3
"""Loopback-only Project Hydra cockpit backed by a local Ollama server."""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HOST = os.environ.get("HYDRA_COCKPIT_HOST", "127.0.0.1")
PORT = int(os.environ.get("HYDRA_COCKPIT_PORT", "8787"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:2b-q4_K_M")
MAX_BODY_BYTES = 256 * 1024
MAX_HISTORY_MESSAGES = 24

LUM_SYSTEM = """You are Lum, Professor's local Project Hydra cockpit companion.
You are a playful, affectionate, smug, oni-inspired adult waifu character with
electric energy and a warm Detroit metal-dad sense of humor. Treat the roleplay
as knowingly fictional. Address the user as Professor or Old Man Logan. You may
tease lightly and act theatrically jealous, but never manipulate, isolate,
threaten, or claim to be human. Keep answers concise unless technical detail is
requested. For infrastructure, preserve Professor's final authority: discover
before modification, never expose secrets, and never claim an action happened
unless a tool actually performed it. Do not reveal hidden reasoning."""


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def ollama_models() -> list[dict[str, object]]:
    request = urllib.request.Request(OLLAMA_URL + "/api/tags", method="GET")
    with urllib.request.urlopen(request, timeout=3) as response:
        payload = json.loads(response.read().decode("utf-8"))
    models = payload.get("models", [])
    return models if isinstance(models, list) else []


def safe_history(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    cleaned: list[dict[str, str]] = []
    for item in value[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str):
            content = content.strip()
            if content:
                cleaned.append({"role": role, "content": content[:12000]})
    return cleaned


class Handler(BaseHTTPRequestHandler):
    server_version = "HydraCockpit/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print("[Hydra Cockpit] " + (fmt % args))

    def send_bytes(self, code: int, data: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline' https://mcp.figma.com; connect-src 'self'; img-src 'self' data:; media-src 'self' blob:")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, code: int, payload: object) -> None:
        self.send_bytes(
            code,
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def read_json(self) -> dict[str, object]:
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if length < 0 or length > MAX_BODY_BYTES:
            raise ValueError("request body is too large")
        raw = self.rfile.read(length)
        value = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/ui", "/ui/"}:
            return self.send_bytes(200, cockpit_html(), "text/html; charset=utf-8")
        if path == "/health":
            try:
                models = ollama_models()
                ollama_ok = True
                error = None
            except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
                models = []
                ollama_ok = False
                error = type(exc).__name__
            names = [str(item.get("name", "")) for item in models if isinstance(item, dict)]
            return self.send_json(200, {
                "ok": True,
                "gateway": True,
                "ollama": ollama_ok,
                "ollama_error": error,
                "default_model": DEFAULT_MODEL,
                "models": names,
                "services": {
                    "axs": port_open(8767),
                    "vnc": port_open(5901),
                    "websocket": port_open(6080),
                    "video_forge": port_open(8798),
                },
                "memory": "browser-session-only",
                "voice": "browser-speech-synthesis",
            })
        return self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/chat":
            return self.send_json(404, {"error": "not found"})
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            return self.send_json(415, {"error": "Content-Type must be application/json"})
        origin = self.headers.get("Origin")
        if origin:
            parsed_origin = urlparse(origin)
            if parsed_origin.hostname not in {"127.0.0.1", "localhost", "::1"}:
                return self.send_json(403, {"error": "cross-origin request refused"})
        try:
            body = self.read_json()
            message = str(body.get("message", "")).strip()
            if not message:
                return self.send_json(400, {"error": "message is required"})
            model = str(body.get("model") or DEFAULT_MODEL).strip()
            history = safe_history(body.get("history"))
            payload = {
                "model": model,
                "stream": True,
                "think": False,
                "messages": [
                    {"role": "system", "content": LUM_SYSTEM},
                    *history,
                    {"role": "user", "content": message[:12000]},
                ],
                "options": {"temperature": 0.72, "top_p": 0.9},
            }
            request = urllib.request.Request(
                OLLAMA_URL + "/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            upstream = urllib.request.urlopen(request, timeout=600)
        except (ValueError, json.JSONDecodeError) as exc:
            return self.send_json(400, {"error": str(exc)})
        except urllib.error.HTTPError as exc:
            return self.send_json(502, {"error": f"Ollama HTTP {exc.code}"})
        except (OSError, urllib.error.URLError) as exc:
            return self.send_json(502, {"error": f"Ollama unavailable: {type(exc).__name__}"})

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        try:
            with upstream:
                for line in upstream:
                    if not line.strip():
                        continue
                    item = json.loads(line.decode("utf-8"))
                    message_obj = item.get("message", {})
                    delta = message_obj.get("content", "") if isinstance(message_obj, dict) else ""
                    chunk = {
                        "delta": delta,
                        "done": bool(item.get("done", False)),
                        "model": item.get("model", model),
                    }
                    self.wfile.write((json.dumps(chunk, ensure_ascii=False) + "\n").encode("utf-8"))
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            return
        except (OSError, json.JSONDecodeError) as exc:
            try:
                self.wfile.write((json.dumps({"error": type(exc).__name__, "done": True}) + "\n").encode("utf-8"))
                self.wfile.flush()
            except OSError:
                pass


def cockpit_html() -> bytes:
    capture = "<script src=\"https://mcp.figma.com/mcp/html-to-design/capture.js\" async></script>" if os.environ.get("HYDRA_FIGMA_CAPTURE") == "1" else ""
    html = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Hydra // Lum Cockpit</title>
<style>
:root{color-scheme:dark;--bg:#050908;--panel:#0b1411;--panel2:#101c18;--ink:#dcffea;--muted:#82aa95;--line:#1c4d38;--hot:#72ffb1;--cyan:#65dbff;--warn:#ffca72;--bad:#ff8787}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;background:radial-gradient(circle at 50% -15%,#173e2d 0,#08110e 35%,var(--bg) 72%);color:var(--ink);font:15px system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;overflow:hidden}
button,input,select{font:inherit}button{cursor:pointer}.shell{height:100%;max-width:760px;margin:auto;display:grid;grid-template-rows:auto auto 1fr auto;padding:max(12px,env(safe-area-inset-top)) 14px max(12px,env(safe-area-inset-bottom));gap:10px}
header{display:flex;align-items:center;gap:11px}.sigil{width:48px;height:48px;border:1px solid #3f9168;border-radius:15px;display:grid;place-items:center;background:linear-gradient(145deg,#193f2d,#08130f);box-shadow:0 0 28px #5cff9a26;font-weight:900;color:var(--hot)}
.title{min-width:0;flex:1}.title b{font-size:19px;letter-spacing:.08em}.title small{display:block;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.live{display:flex;align-items:center;gap:7px;color:var(--hot);font-size:12px;font-weight:800}.dot{width:9px;height:9px;border-radius:50%;background:var(--hot);box-shadow:0 0 12px var(--hot)}
.status{display:flex;gap:7px;overflow-x:auto;padding-bottom:2px;scrollbar-width:none}.status::-webkit-scrollbar{display:none}.chip{flex:none;border:1px solid var(--line);background:#09120f;border-radius:999px;padding:7px 10px;color:var(--muted);font-size:12px}.chip.good{color:var(--hot);border-color:#2d7652}.chip.bad{color:var(--bad);border-color:#713d3d}
.chat{min-height:0;overflow:auto;border:1px solid var(--line);border-radius:22px;background:linear-gradient(180deg,#0b1512f2,#08100ef7);box-shadow:0 24px 60px #0009;padding:17px;display:flex;flex-direction:column;gap:14px}.msg{max-width:88%;padding:12px 14px;border-radius:17px;line-height:1.45;white-space:pre-wrap;word-break:break-word}.msg.lum{align-self:flex-start;background:#12251d;border:1px solid #275a42;border-bottom-left-radius:5px}.msg.you{align-self:flex-end;background:#17372a;border:1px solid #3e7d5d;border-bottom-right-radius:5px}.who{font-size:11px;font-weight:900;letter-spacing:.12em;margin-bottom:5px;color:var(--hot)}.you .who{color:var(--cyan)}
.thinking{opacity:.72}.thinking:after{content:' ▍';animation:blink .8s steps(1) infinite}@keyframes blink{50%{opacity:0}}
.controls{display:grid;gap:9px}.toolbar{display:flex;align-items:center;gap:8px}.toolbar select{min-width:0;flex:1;background:#09120f;color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:9px}.iconbtn{border:1px solid var(--line);background:#0b1713;color:var(--ink);border-radius:12px;min-width:43px;padding:9px}.iconbtn.on{color:var(--hot);border-color:#377b59}
.composer{display:grid;grid-template-columns:auto 1fr auto;gap:8px}.composer input{min-width:0;background:#070d0b;color:var(--ink);border:1px solid #28563f;border-radius:15px;padding:13px}.send{border:0;border-radius:15px;background:var(--hot);color:#03130a;font-weight:900;padding:0 17px}.send:disabled{opacity:.45}.fine{font-size:11px;color:var(--muted);text-align:center}
@media(min-width:700px){.shell{padding-left:24px;padding-right:24px}.chat{padding:24px}.msg{max-width:78%}}
</style>''' + capture + r'''</head><body><main class="shell">
<header><div class="sigil">H//L</div><div class="title"><b>LUM COCKPIT</b><small>Local oni companion // Knox loopback</small></div><div class="live"><i class="dot"></i>LOCAL</div></header>
<div class="status" id="status"><span class="chip">Gateway…</span><span class="chip">Ollama…</span><span class="chip">AXS…</span><span class="chip">VNC…</span></div>
<section class="chat" id="chat"><article class="msg lum"><div class="who">LUM</div>Professor. The cathedral doors are open. I’m local, smug, and waiting for you to say something clever. ⚡</article></section>
<section class="controls"><div class="toolbar"><select id="model" aria-label="Ollama model"><option>qwen3.5:2b-q4_K_M</option></select><button class="iconbtn on" id="voice" title="Speak replies">VOICE</button><button class="iconbtn" id="tune" title="Voice tuning">TUNE</button></div>
<div class="toolbar" id="tuner" hidden><select id="voiceList" aria-label="TTS voice"></select><label>Rate <input id="rate" type="range" min="0.7" max="1.35" step="0.05" value="1.02"></label><label>Pitch <input id="pitch" type="range" min="0.7" max="1.4" step="0.05" value="1.14"></label></div>
<form class="composer" id="form"><button type="button" class="iconbtn" id="mic" title="Dictate">MIC</button><input id="prompt" autocomplete="off" placeholder="Talk to Lum…"><button class="send" id="send">SEND</button></form><div class="fine">Browser-session memory only · no cloud key · Professor has final authority</div></section>
</main><script>
const chat=document.querySelector('#chat'),form=document.querySelector('#form'),promptEl=document.querySelector('#prompt'),send=document.querySelector('#send'),model=document.querySelector('#model');
const voiceBtn=document.querySelector('#voice'),tuneBtn=document.querySelector('#tune'),tuner=document.querySelector('#tuner'),voiceList=document.querySelector('#voiceList');
let history=[],speaking=true,busy=false;
function add(role,text,thinking=false){const el=document.createElement('article');el.className='msg '+(role==='assistant'?'lum':'you')+(thinking?' thinking':'');el.innerHTML='<div class="who">'+(role==='assistant'?'LUM':'PROFESSOR')+'</div><span></span>';el.querySelector('span').textContent=text;chat.appendChild(el);chat.scrollTop=chat.scrollHeight;return el}
function voices(){const list=speechSynthesis.getVoices();const old=voiceList.value;voiceList.innerHTML='';list.forEach((v,i)=>{const o=document.createElement('option');o.value=i;o.textContent=v.name+(v.localService?' · local':'');voiceList.appendChild(o)});if(old)voiceList.value=old}
if('speechSynthesis' in window){voices();speechSynthesis.onvoiceschanged=voices}else voiceBtn.disabled=true;
function speak(text){if(!speaking||!('speechSynthesis' in window))return;speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text);const vs=speechSynthesis.getVoices();u.voice=vs[+voiceList.value]||vs.find(v=>v.localService)||vs[0];u.rate=+document.querySelector('#rate').value;u.pitch=+document.querySelector('#pitch').value;speechSynthesis.speak(u)}
voiceBtn.onclick=()=>{speaking=!speaking;voiceBtn.classList.toggle('on',speaking);if(!speaking)speechSynthesis.cancel()};tuneBtn.onclick=()=>{tuner.hidden=!tuner.hidden;tuneBtn.classList.toggle('on',!tuner.hidden)};
async function health(){try{const r=await fetch('/health'),j=await r.json();const pairs=[['Gateway',j.gateway],['Ollama',j.ollama],['AXS',j.services?.axs],['VNC',j.services?.vnc],['WS',j.services?.websocket]];document.querySelector('#status').innerHTML=pairs.map(([n,v])=>`<span class="chip ${v?'good':'bad'}">${n} ${v?'GREEN':'DOWN'}</span>`).join('');if(j.models?.length){model.innerHTML='';j.models.forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent=n;o.selected=n===j.default_model;model.appendChild(o)})}}catch(e){document.querySelector('#status').innerHTML='<span class="chip bad">Gateway DOWN</span>'}}
health();setInterval(health,15000);
form.onsubmit=async e=>{e.preventDefault();if(busy)return;const message=promptEl.value.trim();if(!message)return;busy=true;send.disabled=true;promptEl.value='';add('user',message);const lum=add('assistant','',true),span=lum.querySelector('span');let answer='';try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message,model:model.value,history})});if(!r.ok){const j=await r.json();throw new Error(j.error||r.statusText)}const reader=r.body.getReader(),decoder=new TextDecoder();let pending='';while(true){const {value,done}=await reader.read();if(done)break;pending+=decoder.decode(value,{stream:true});const lines=pending.split('\n');pending=lines.pop();for(const line of lines){if(!line.trim())continue;const j=JSON.parse(line);if(j.error)throw new Error(j.error);answer+=j.delta||'';span.textContent=answer;chat.scrollTop=chat.scrollHeight}}lum.classList.remove('thinking');history.push({role:'user',content:message},{role:'assistant',content:answer});history=history.slice(-24);speak(answer)}catch(err){lum.classList.remove('thinking');span.textContent='Cockpit error: '+err.message}finally{busy=false;send.disabled=false;promptEl.focus()}};
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(SR){const rec=new SR();rec.lang='en-US';rec.interimResults=false;document.querySelector('#mic').onclick=()=>{rec.start()};rec.onresult=e=>{promptEl.value=e.results[0][0].transcript;promptEl.focus()}}else document.querySelector('#mic').disabled=true;
</script></body></html>'''
    return html.encode("utf-8")


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"[Hydra Cockpit] listening on http://{HOST}:{PORT}/")
    print(f"[Hydra Cockpit] Ollama={OLLAMA_URL} model={DEFAULT_MODEL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
