#!/usr/bin/env python3
"""KAI 9000 loopback-only FFmpeg worker with Ollama-assisted planning."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request
from urllib.parse import urlparse
import json
import os
import shutil
import subprocess
import threading
import time
import uuid

HOST = "127.0.0.1"
PORT = 8001
OLLAMA = "http://127.0.0.1:11434"
MODEL = os.environ.get("KAI_MODEL", "qwen2.5:0.5b")
ROOT = os.path.realpath(os.path.expanduser("~/kai9000"))
SANDBOX = os.path.realpath(os.path.join(ROOT, "sandbox"))
STATE = os.path.join(ROOT, "state", "ffmpeg")
OUTPUT = os.path.join(STATE, "output")
LOGS = os.path.join(ROOT, "logs", "ffmpeg")
JOBS = {}
LOCK = threading.Lock()

PRESETS = {
    "proof_360p": ["-vf", "scale=-2:360", "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"],
    "samsung_mp4": ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"],
    "audio_wav": ["-vn", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2"],
    "audio_opus": ["-vn", "-c:a", "libopus", "-b:a", "160k"],
}


def ensure_dirs():
    for path in (STATE, OUTPUT, LOGS):
        os.makedirs(path, exist_ok=True)


def safe_input(value):
    path = os.path.realpath(os.path.expanduser(str(value)))
    if not (path == SANDBOX or path.startswith(SANDBOX + os.sep)):
        raise ValueError("input must be inside KAI9000_SANDBOX")
    if not os.path.isfile(path):
        raise ValueError("input file not found")
    return path


def job_snapshot(job):
    return {key: value for key, value in job.items() if key != "command"}


def run_job(job_id, command):
    log_path = os.path.join(LOGS, job_id + ".log")
    with LOCK:
        JOBS[job_id]["status"] = "running"
        JOBS[job_id]["started_at"] = int(time.time())
    try:
        with open(log_path, "wb") as log:
            completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=3600, check=False)
        status = "complete" if completed.returncode == 0 else "failed"
        error = None if completed.returncode == 0 else "ffmpeg_exit_%d" % completed.returncode
    except subprocess.TimeoutExpired:
        status, error = "failed", "timeout"
    except Exception as exc:
        status, error = "failed", str(exc)
    with LOCK:
        JOBS[job_id].update(status=status, error=error, finished_at=int(time.time()), log=log_path)


def ollama_plan(instruction):
    system = """Return JSON only. Select exactly one preset: proof_360p, samsung_mp4, audio_wav, or audio_opus. Schema: {\"preset\":string,\"reason\":string}. Never emit shell commands, paths, flags, or extra keys."""
    payload = json.dumps({"model": MODEL, "stream": False, "format": "json", "messages": [{"role": "system", "content": system}, {"role": "user", "content": instruction}], "options": {"temperature": 0}}).encode()
    req = request.Request(OLLAMA + "/api/chat", data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=90) as response:
        outer = json.loads(response.read().decode())
    plan = json.loads(outer.get("message", {}).get("content", "{}"))
    preset = plan.get("preset")
    if preset not in PRESETS:
        raise ValueError("Ollama returned unsupported preset")
    return {"preset": preset, "reason": str(plan.get("reason", ""))[:500], "model": MODEL}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, obj, status=200):
        body = json.dumps(obj, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size < 1 or size > 1048576:
            raise ValueError("invalid body size")
        return json.loads(self.rfile.read(size).decode())

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.send_json({"status": "green", "service": "KAI 9000 Media Forge", "ffmpeg": shutil.which("ffmpeg"), "ffprobe": shutil.which("ffprobe"), "ollama": OLLAMA, "presets": sorted(PRESETS), "output": OUTPUT})
            return
        if path == "/api/media/jobs":
            with LOCK:
                rows = [job_snapshot(job) for job in JOBS.values()]
            self.send_json({"jobs": rows})
            return
        if path.startswith("/api/media/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            with LOCK:
                job = JOBS.get(job_id)
                result = job_snapshot(job) if job else None
            self.send_json(result or {"error": "not_found"}, 200 if result else 404)
            return
        self.send_json({"error": "not_found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            incoming = self.read_json()
            if path == "/api/media/plan":
                instruction = str(incoming.get("instruction", "")).strip()
                if not instruction or len(instruction) > 2000:
                    raise ValueError("invalid instruction")
                self.send_json({"status": "planned", "plan": ollama_plan(instruction)})
                return
            if path == "/api/media/probe":
                source = safe_input(incoming.get("input", ""))
                command = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", source]
                result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
                if result.returncode != 0:
                    self.send_json({"error": "probe_failed", "detail": result.stderr[-1000:]}, 422)
                else:
                    self.send_json(json.loads(result.stdout))
                return
            if path == "/api/media/jobs":
                source = safe_input(incoming.get("input", ""))
                preset = str(incoming.get("preset", ""))
                if preset not in PRESETS:
                    raise ValueError("unsupported preset")
                extension = ".wav" if preset == "audio_wav" else ".opus" if preset == "audio_opus" else ".mp4"
                job_id = uuid.uuid4().hex
                target = os.path.join(OUTPUT, job_id + extension)
                command = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", source] + PRESETS[preset] + [target]
                job = {"id": job_id, "status": "queued", "preset": preset, "input": source, "output": target, "created_at": int(time.time()), "error": None, "command": command}
                with LOCK:
                    JOBS[job_id] = job
                threading.Thread(target=run_job, args=(job_id, command), daemon=True).start()
                self.send_json(job_snapshot(job), 202)
                return
            self.send_json({"error": "not_found"}, 404)
        except ValueError as exc:
            self.send_json({"error": "invalid_request", "detail": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": "server_error", "detail": str(exc)}, 500)

    def log_message(self, fmt, *args):
        print("[KAI-MEDIA]", fmt % args, flush=True)


if __name__ == "__main__":
    ensure_dirs()
    print("KAI 9000 Media Forge: http://%s:%d" % (HOST, PORT), flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
