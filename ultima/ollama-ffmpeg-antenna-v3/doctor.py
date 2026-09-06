from __future__ import annotations
import importlib.util, os, platform, shutil, sys

print("python:", sys.version.split()[0])
print("platform:", platform.platform())
for name in ("ffmpeg", "ffprobe", "rclone"):
    print(f"{name}:", shutil.which(name) or "missing/optional")
for module in ("fastapi", "httpx"):
    print(f"{module}:", "yes" if importlib.util.find_spec(module) else "no")
print("COMFYUI_URL:", os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188"))
print("RCLONE_REMOTE:", os.environ.get("RCLONE_REMOTE", "drive:"))
print("RCLONE_DEST:", os.environ.get("RCLONE_DEST", "not configured"))
