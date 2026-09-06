from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME = REPO_ROOT / "ultima" / "ollama-ffmpeg-antenna-v3"
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
EDGE_REPO_URL = "https://api.github.com/repos/google-ai-edge/gallery"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def get_json(url: str, *, timeout: float = 20.0) -> tuple[int, dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": "KAI9000-remote-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"body": body[:500]}
        return int(exc.code), payload


def get_text(url: str, *, timeout: float = 20.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "KAI9000-remote-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="replace")


def check_openai_gateway() -> dict[str, Any]:
    status, payload = get_json(OPENAI_MODELS_URL)
    reachable = status in {200, 401, 403, 429}
    if not reachable:
        raise RuntimeError(f"OpenAI API gateway smoke failed with HTTP {status}")
    return {
        "ok": True,
        "url": OPENAI_MODELS_URL,
        "http_status_without_credentials": status,
        "expected_auth_boundary_observed": status in {401, 403},
        "error_type": ((payload.get("error") or {}).get("type") if isinstance(payload, dict) else None),
    }


def check_edge_gallery() -> dict[str, Any]:
    status, repo = get_json(EDGE_REPO_URL)
    if status != 200 or repo.get("full_name") != "google-ai-edge/gallery":
        raise RuntimeError(f"AI Edge Gallery repository smoke failed: HTTP {status}")
    branch = str(repo.get("default_branch") or "main")
    raw_url = f"https://raw.githubusercontent.com/google-ai-edge/gallery/{urllib.parse.quote(branch, safe='')}/README.md"
    readme_status, readme = get_text(raw_url)
    if readme_status != 200 or "Google AI Edge Gallery" not in readme:
        raise RuntimeError(f"AI Edge Gallery README smoke failed: HTTP {readme_status}")
    return {
        "ok": True,
        "repository": repo["full_name"],
        "default_branch": branch,
        "archived": bool(repo.get("archived")),
        "readme_signature": "Google AI Edge Gallery",
        "scope": "public source/integration contract; not Android on-device inference",
    }


class FakeComfy:
    def __init__(self) -> None:
        self.state: dict[str, Any] = {"png": b"", "prompt_id": "kai-smoke-prompt"}
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def _json(self, payload: dict[str, Any], status: int = 200) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path == "/system_stats":
                    self._json({"system": {"fake": True}, "devices": []})
                    return
                if parsed.path == f"/history/{owner.state['prompt_id']}":
                    self._json({
                        owner.state["prompt_id"]: {
                            "outputs": {
                                "9": {
                                    "images": [{
                                        "filename": "kai-smoke-output.png",
                                        "subfolder": "",
                                        "type": "output",
                                    }]
                                }
                            }
                        }
                    })
                    return
                if parsed.path == "/view":
                    body = owner.state["png"]
                    if not body:
                        self.send_error(503, "smoke PNG not seeded")
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "image/png")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                self.send_error(404)

            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0") or "0")
                if length:
                    self.rfile.read(length)
                if self.path == "/upload/image":
                    self._json({"name": "kai-smoke-input.png", "subfolder": "", "type": "input"})
                    return
                if self.path == "/prompt":
                    self._json({"prompt_id": owner.state["prompt_id"]})
                    return
                self.send_error(404)

            def log_message(self, fmt: str, *args: object) -> None:
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        host, port = self.server.server_address[:2]
        return f"http://{host}:{port}"

    def __enter__(self) -> "FakeComfy":
        self.thread.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def ffprobe_json(path: Path) -> dict[str, Any]:
    proc = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ])
    return json.loads(proc.stdout)


def check_media_service(workdir: Path, fake_comfy: FakeComfy) -> dict[str, Any]:
    os.environ["KAI_WORK_ROOT"] = str(workdir / "jobs")
    os.environ["COMFYUI_URL"] = fake_comfy.url
    os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:11434")
    os.environ.setdefault("OLLAMA_MODEL", "qwen2.5:3b")

    sys.path.insert(0, str(RUNTIME))
    from fastapi.testclient import TestClient
    import magic_server

    client = TestClient(magic_server.APP)

    source = workdir / "source.mp4"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=30",
        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
        "-t", "2",
        "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k",
        str(source),
    ])

    health = client.get("/health")
    health.raise_for_status()
    health_json = health.json()
    if not health_json.get("ok") or not health_json.get("ffmpeg"):
        raise RuntimeError("KAI media service health did not report FFmpeg")

    magic_payload: dict[str, Any] = {
        "message": "Smoke-test the 24 fps MP4 demux, guided frame regeneration, APNG preview, and remux lane. Reply concisely."
    }
    if os.environ.get("OPENAI_API_KEY"):
        magic_payload["model"] = os.environ.get("OPENAI_SMOKE_MODEL", "gpt-5.6-luna")
    magic = client.post("/api/magic/chat", json=magic_payload)
    magic.raise_for_status()
    magic_json = magic.json()
    expected_mode = "openai" if os.environ.get("OPENAI_API_KEY") else "deterministic_mock"
    if magic_json.get("mode") != expected_mode or not magic_json.get("assistant"):
        raise RuntimeError(f"Magic planner smoke failed: {magic_json}")

    demux = client.post("/api/demux", json={"source_mp4": str(source), "label": "remote-ai-smoke"})
    demux.raise_for_status()
    demux_json = demux.json()
    job_id = demux_json["job_id"]
    frame_count = int(demux_json.get("frames_extracted", 0))
    if not 47 <= frame_count <= 49:
        raise RuntimeError(f"Expected about 48 frames at 24 fps for 2 seconds; got {frame_count}")

    job_root = Path(os.environ["KAI_WORK_ROOT"]) / job_id
    first_frame = job_root / "cache" / "frames_in" / "00000001.png"
    if not first_frame.is_file():
        raise RuntimeError("Demux did not create frame 00000001.png")
    fake_comfy.state["png"] = first_frame.read_bytes()

    apng = client.post("/api/apng", json={"job_id": job_id, "use_ai_frames": False, "fps": 12, "loop": 0})
    apng.raise_for_status()
    apng_json = apng.json()
    apng_path = Path(apng_json["apng"])
    if not apng_path.is_file() or apng_path.stat().st_size <= 0:
        raise RuntimeError("APNG preview was not created")

    comfy_cfg = client.post("/api/comfy/configure", json={
        "job_id": job_id,
        "workflow_api": {"1": {"class_type": "LoadImage", "inputs": {"image": "placeholder.png"}}},
        "image_nodes": {"current": "1"},
        "text_overrides": {},
    })
    comfy_cfg.raise_for_status()

    regen = client.post("/api/comfy/regen", json={
        "job_id": job_id,
        "start_frame": 1,
        "end_frame": 1,
        "step": 1,
        "timeout_s": 30,
    })
    regen.raise_for_status()
    regen_json = regen.json()
    if regen_json.get("frames_regenerated") != 1:
        raise RuntimeError(f"Expected one regenerated frame; got {regen_json}")

    remux = client.post("/api/remux", json={
        "job_id": job_id,
        "use_ai_frames": True,
        "crf": 23,
        "preset": "veryfast",
    })
    remux.raise_for_status()
    remux_json = remux.json()
    remux_path = Path(remux_json["mp4"])
    if not remux_path.is_file() or remux_path.stat().st_size <= 0:
        raise RuntimeError("Remux MP4 was not created")

    probe = ffprobe_json(remux_path)
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not video or video.get("codec_name") != "h264" or video.get("r_frame_rate") != "24/1":
        raise RuntimeError(f"Remux video contract failed: {video}")
    if not audio:
        raise RuntimeError("Remux lost the source audio stream")

    seal = client.post("/api/seal", json={"job_id": job_id, "include_source_mp4": False})
    seal.raise_for_status()
    seal_json = seal.json()
    if not seal_json.get("seal", {}).get("artifacts"):
        raise RuntimeError("Output seal contains no artifacts")

    return {
        "ok": True,
        "service_health": {
            "ffmpeg": bool(health_json.get("ffmpeg")),
            "ffprobe": bool(health_json.get("ffprobe")),
            "comfyui_fake_contract": bool(health_json.get("comfyui_ok")),
        },
        "magic_planner": {
            "mode": magic_json.get("mode"),
            "model": magic_json.get("model"),
            "live_openai_inference": magic_json.get("mode") == "openai",
        },
        "media": {
            "job_id": job_id,
            "source_seconds": 2,
            "frames_extracted": frame_count,
            "target_fps": 24,
            "apng_bytes": apng_path.stat().st_size,
            "frames_regenerated_via_comfy_contract": 1,
            "remux_bytes": remux_path.stat().st_size,
            "video_codec": video.get("codec_name"),
            "video_rate": video.get("r_frame_rate"),
            "audio_codec": audio.get("codec_name"),
            "sealed_artifact_count": len(seal_json["seal"]["artifacts"]),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="kai9000-remote-smoke-report.json")
    args = ap.parse_args()

    report: dict[str, Any] = {
        "schema": "kai9000.remote-ai-media-smoke.v1",
        "created_unix": int(time.time()),
        "github": {
            "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
            "sha": os.environ.get("GITHUB_SHA"),
            "ref": os.environ.get("GITHUB_REF"),
            "runner": bool(os.environ.get("GITHUB_ACTIONS")),
        },
    }

    report["openai_gateway"] = check_openai_gateway()
    report["edge_gallery"] = check_edge_gallery()

    with tempfile.TemporaryDirectory(prefix="kai9000-remote-smoke-") as temp:
        with FakeComfy() as fake_comfy:
            report["kai9000_media"] = check_media_service(Path(temp), fake_comfy)

    report["overall"] = "GREEN"
    out = Path(args.report).resolve()
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"REMOTE AI MEDIA SMOKE GREEN: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
