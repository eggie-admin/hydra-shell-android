from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from comfy_batch import ComfyClient, regenerate_frames
from drive_backup import backup_files
from antenna import AntennaError, antenna_status, ollama_chat

APP = FastAPI(title="KAI9000 Ultima Ollama FFmpeg Antenna", version="3.0.0")
WORK_ROOT = Path(os.environ.get("KAI_WORK_ROOT", "./data/jobs")).resolve()
WORK_ROOT.mkdir(parents=True, exist_ok=True)
COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
FPS = 24
FRAME_PATTERN = "%08d.png"


def require_bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise HTTPException(status_code=503, detail=f"Missing required binary: {name}")
    return path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def root_for(job_id: str) -> Path:
    return (WORK_ROOT / job_id).resolve()


def layout(job_id: str) -> dict[str, Path]:
    root = root_for(job_id)
    p = {
        "root": root,
        "input": root / "input",
        "frames_in": root / "cache" / "frames_in",
        "frames_ai": root / "cache" / "frames_ai",
        "audio": root / "cache" / "audio",
        "meta": root / "cache" / "meta",
        "preview": root / "preview",
        "output": root / "output",
    }
    for d in p.values():
        d.mkdir(parents=True, exist_ok=True)
    return p


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class DemuxRequest(BaseModel):
    source_mp4: str = Field(min_length=1)
    label: str = Field(default="ultima-job", min_length=1, max_length=120)


class ApngRequest(BaseModel):
    job_id: str
    use_ai_frames: bool = False
    fps: int = Field(default=12, ge=1, le=24)
    loop: int = Field(default=0, ge=0)


class ComfyConfigureRequest(BaseModel):
    job_id: str
    workflow_api: dict
    image_nodes: dict[str, str] = Field(default_factory=lambda: {"current": "1"})
    text_overrides: dict[str, str] = Field(default_factory=dict)


class ComfyRegenRequest(BaseModel):
    job_id: str
    start_frame: int | None = None
    end_frame: int | None = None
    step: int = Field(default=1, ge=1, le=120)
    timeout_s: int = Field(default=900, ge=30, le=7200)


class RemuxRequest(BaseModel):
    job_id: str
    use_ai_frames: bool = True
    crf: int = Field(default=18, ge=0, le=35)
    preset: str = Field(default="medium")


class SealRequest(BaseModel):
    job_id: str
    include_source_mp4: bool = False


class BackupRequest(BaseModel):
    job_id: str
    include_source_mp4: bool = False


class AntennaChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    model: str | None = None


APP.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")


@APP.get("/health")
def health():
    comfy = None
    try:
        comfy = ComfyClient(COMFYUI_URL, timeout=5).health()
        comfy_ok = True
    except Exception as exc:
        comfy_ok = False
        comfy = str(exc)
    return {
        "ok": True,
        "service": "kai9000-ultima-ollama-ffmpeg-antenna-v3",
        "antenna": antenna_status(),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "rclone": shutil.which("rclone"),
        "comfyui_url": COMFYUI_URL,
        "comfyui_ok": comfy_ok,
        "comfyui": comfy,
    }


@APP.get("/api/antenna/status")
def api_antenna_status():
    return antenna_status()


@APP.post("/api/antenna/ollama/chat")
def api_antenna_ollama_chat(req: AntennaChatRequest):
    try:
        return ollama_chat(req.message, req.model)
    except AntennaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@APP.get("/preview", response_class=HTMLResponse)
def preview_page():
    return HTMLResponse((Path(__file__).resolve().parent / "static" / "index.html").read_text(encoding="utf-8"))


@APP.post("/api/demux")
def demux(req: DemuxRequest):
    ffmpeg, ffprobe = require_bin("ffmpeg"), require_bin("ffprobe")
    src = Path(req.source_mp4).expanduser().resolve()
    if not src.is_file():
        raise HTTPException(status_code=404, detail=f"Source not found: {src}")
    job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    p = layout(job_id)
    target = p["input"] / "source.mp4"
    shutil.copy2(src, target)

    probe = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(target)], check=True, capture_output=True, text=True)
    (p["meta"] / "ffprobe.json").write_text(probe.stdout, encoding="utf-8")

    audio_target = p["audio"] / "source_audio.mka"
    try:
        run([ffmpeg, "-y", "-i", str(target), "-map", "0:a?", "-c", "copy", str(audio_target)])
        audio_cached = True
    except subprocess.CalledProcessError:
        audio_target.unlink(missing_ok=True)
        audio_cached = False

    run([ffmpeg, "-y", "-i", str(target), "-map", "0:v:0", "-vf", f"fps={FPS}", "-vsync", "0", str(p["frames_in"] / FRAME_PATTERN)])
    count = 0
    with (p["meta"] / "frame_map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["frame", "filename", "status"])
        for frame in sorted(p["frames_in"].glob("*.png")):
            shutil.copy2(frame, p["frames_ai"] / frame.name)
            w.writerow([frame.stem, frame.name, "seeded"]); count += 1

    payload = {
        "schema": "kai9000.ultima-job.v2",
        "job_id": job_id,
        "label": req.label,
        "target_fps": FPS,
        "frames_extracted": count,
        "audio_cached": audio_cached,
        "source_sha256": sha256(target),
        "status": "demux_complete",
    }
    write_json(p["root"] / "job_manifest.json", payload)
    return payload


@APP.post("/api/apng")
def apng(req: ApngRequest):
    ffmpeg = require_bin("ffmpeg")
    p = layout(req.job_id)
    source = p["frames_ai"] if req.use_ai_frames else p["frames_in"]
    if not any(source.glob("*.png")):
        raise HTTPException(status_code=400, detail="No frames")
    out = p["preview"] / ("preview_ai.apng" if req.use_ai_frames else "preview_source.apng")
    run([ffmpeg, "-y", "-framerate", str(req.fps), "-i", str(source / FRAME_PATTERN), "-plays", str(req.loop), "-f", "apng", str(out)])
    return {"ok": True, "apng": str(out), "sha256": sha256(out), "download": f"/api/file/{req.job_id}/{out.relative_to(p['root']).as_posix()}"}


@APP.post("/api/comfy/configure")
def comfy_configure(req: ComfyConfigureRequest):
    p = layout(req.job_id)
    if not (p["root"] / "job_manifest.json").is_file():
        raise HTTPException(status_code=404, detail="Unknown job")
    cfg = {"workflow_api": req.workflow_api, "image_nodes": req.image_nodes, "text_overrides": req.text_overrides}
    path = p["meta"] / "comfy_config.json"
    write_json(path, cfg)
    return {"ok": True, "config": str(path), "roles": list(req.image_nodes.keys())}


@APP.post("/api/comfy/regen")
def comfy_regen(req: ComfyRegenRequest):
    p = layout(req.job_id)
    config_path = p["meta"] / "comfy_config.json"
    if not config_path.is_file():
        raise HTTPException(status_code=400, detail="Configure ComfyUI workflow first")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    try:
        results = regenerate_frames(
            comfy_url=COMFYUI_URL,
            workflow_api=cfg["workflow_api"],
            frames_in=p["frames_in"],
            frames_ai=p["frames_ai"],
            image_nodes=cfg["image_nodes"],
            text_overrides=cfg.get("text_overrides") or {},
            start_frame=req.start_frame,
            end_frame=req.end_frame,
            step=req.step,
            timeout_s=req.timeout_s,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    report = p["meta"] / "comfy_regen_report.json"
    write_json(report, {"results": results})
    return {"ok": True, "frames_regenerated": len(results), "report": str(report)}


@APP.post("/api/remux")
def remux(req: RemuxRequest):
    ffmpeg = require_bin("ffmpeg")
    p = layout(req.job_id)
    source = p["frames_ai"] if req.use_ai_frames else p["frames_in"]
    if not any(source.glob("*.png")):
        raise HTTPException(status_code=400, detail="No frames")
    out = p["output"] / ("remux_ai_24fps.mp4" if req.use_ai_frames else "remux_source_24fps.mp4")
    audio = p["audio"] / "source_audio.mka"
    if audio.is_file():
        cmd = [ffmpeg, "-y", "-framerate", str(FPS), "-i", str(source / FRAME_PATTERN), "-i", str(audio), "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264", "-preset", req.preset, "-crf", str(req.crf), "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)]
    else:
        cmd = [ffmpeg, "-y", "-framerate", str(FPS), "-i", str(source / FRAME_PATTERN), "-i", str(p["input"] / "source.mp4"), "-map", "0:v:0", "-map", "1:a?", "-c:v", "libx264", "-preset", req.preset, "-crf", str(req.crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    run(cmd)
    return {"ok": True, "mp4": str(out), "sha256": sha256(out), "download": f"/api/file/{req.job_id}/{out.relative_to(p['root']).as_posix()}"}


def artifact_list(job_id: str, include_source: bool) -> list[Path]:
    p = layout(job_id)
    candidates = [
        p["root"] / "job_manifest.json",
        p["meta"] / "ffprobe.json",
        p["meta"] / "frame_map.csv",
        p["meta"] / "comfy_config.json",
        p["meta"] / "comfy_regen_report.json",
        p["preview"] / "preview_source.apng",
        p["preview"] / "preview_ai.apng",
        p["output"] / "remux_source_24fps.mp4",
        p["output"] / "remux_ai_24fps.mp4",
    ]
    if include_source:
        candidates.append(p["input"] / "source.mp4")
    return [x for x in candidates if x.is_file()]


@APP.post("/api/seal")
def seal(req: SealRequest):
    p = layout(req.job_id)
    artifacts = artifact_list(req.job_id, req.include_source_mp4)
    if not artifacts:
        raise HTTPException(status_code=404, detail="No job artifacts")
    payload = {
        "schema": "kai9000.ultima-output-seal.v1",
        "job_id": req.job_id,
        "created_unix": int(time.time()),
        "artifacts": [
            {"path": str(x.relative_to(p["root"])), "bytes": x.stat().st_size, "sha256": sha256(x)}
            for x in artifacts
        ],
    }
    seal_path = p["root"] / "OUTPUT_SEAL.json"
    write_json(seal_path, payload)
    return {"ok": True, "seal": payload, "download": f"/api/file/{req.job_id}/OUTPUT_SEAL.json"}


@APP.post("/api/backup")
def backup(req: BackupRequest):
    p = layout(req.job_id)
    seal_path = p["root"] / "OUTPUT_SEAL.json"
    if not seal_path.is_file():
        seal(SealRequest(job_id=req.job_id, include_source_mp4=req.include_source_mp4))
    artifacts = artifact_list(req.job_id, req.include_source_mp4) + [seal_path]
    try:
        copied = backup_files(req.job_id, artifacts)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    report = {"schema": "kai9000.drive-backup-report.v1", "job_id": req.job_id, "copied": copied, "created_unix": int(time.time())}
    write_json(p["root"] / "DRIVE_BACKUP_REPORT.json", report)
    return {"ok": True, **report}


@APP.get("/api/jobs")
def jobs():
    return {"ok": True, "jobs": [x.name for x in sorted(WORK_ROOT.glob("*")) if x.is_dir()]}


@APP.get("/api/file/{job_id}/{relpath:path}")
def get_file(job_id: str, relpath: str):
    root = root_for(job_id)
    target = (root / relpath).resolve()
    if not str(target).startswith(str(root)) or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(APP, host="127.0.0.1", port=int(os.environ.get("PORT", "8797")))
