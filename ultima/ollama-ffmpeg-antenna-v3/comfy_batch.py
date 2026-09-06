from __future__ import annotations

import copy
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx


def _base_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("COMFYUI_URL must be an http(s) URL")
    if parsed.username or parsed.password:
        raise ValueError("Do not embed credentials in COMFYUI_URL")
    return url.rstrip("/")


class ComfyClient:
    def __init__(self, base_url: str, timeout: float = 120.0):
        self.base = _base_url(base_url)
        self.client = httpx.Client(timeout=timeout)

    def health(self) -> dict:
        r = self.client.get(f"{self.base}/system_stats")
        r.raise_for_status()
        return r.json()

    def upload_image(self, path: Path) -> str:
        with path.open("rb") as f:
            r = self.client.post(
                f"{self.base}/upload/image",
                files={"image": (path.name, f, "image/png")},
                data={"type": "input", "overwrite": "true"},
            )
        r.raise_for_status()
        payload = r.json()
        name = payload.get("name") or path.name
        subfolder = payload.get("subfolder") or ""
        return f"{subfolder}/{name}".lstrip("/") if subfolder else name

    def queue_prompt(self, workflow: dict) -> str:
        r = self.client.post(f"{self.base}/prompt", json={"prompt": workflow})
        r.raise_for_status()
        payload = r.json()
        prompt_id = payload.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI returned no prompt_id: {payload}")
        return prompt_id

    def history(self, prompt_id: str) -> dict:
        r = self.client.get(f"{self.base}/history/{prompt_id}")
        r.raise_for_status()
        return r.json()

    def wait_for_output(self, prompt_id: str, timeout_s: int = 900, poll_s: float = 1.0) -> dict:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            payload = self.history(prompt_id)
            entry = payload.get(prompt_id)
            if entry and entry.get("outputs"):
                return entry
            time.sleep(poll_s)
        raise TimeoutError(f"Timed out waiting for ComfyUI prompt {prompt_id}")

    def first_output_image(self, entry: dict) -> dict:
        for node_output in (entry.get("outputs") or {}).values():
            images = node_output.get("images") if isinstance(node_output, dict) else None
            if images:
                return images[0]
        raise RuntimeError("ComfyUI history contained no output image")

    def download_image(self, image: dict, dest: Path) -> None:
        params = {
            "filename": image["filename"],
            "subfolder": image.get("subfolder", ""),
            "type": image.get("type", "output"),
        }
        r = self.client.get(f"{self.base}/view", params=params)
        r.raise_for_status()
        dest.write_bytes(r.content)


def _set_image(workflow: dict, node_id: str, image_name: str) -> None:
    node = workflow.get(str(node_id))
    if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict):
        raise KeyError(f"Invalid image node id: {node_id}")
    node["inputs"]["image"] = image_name


def _set_text(workflow: dict, node_id: str, text: str) -> None:
    node = workflow.get(str(node_id))
    if not isinstance(node, dict) or not isinstance(node.get("inputs"), dict):
        raise KeyError(f"Invalid text node id: {node_id}")
    node["inputs"]["text"] = text


def regenerate_frames(
    *,
    comfy_url: str,
    workflow_api: dict,
    frames_in: Path,
    frames_ai: Path,
    image_nodes: dict[str, str],
    text_overrides: dict[str, str] | None = None,
    start_frame: int | None = None,
    end_frame: int | None = None,
    step: int = 1,
    timeout_s: int = 900,
) -> list[dict]:
    client = ComfyClient(comfy_url)
    frames = sorted(p for p in frames_in.glob("*.png") if p.stem.isdigit())
    if not frames:
        raise RuntimeError("No input PNG frames")

    results = []
    for i, current in enumerate(frames):
        n = int(current.stem)
        if start_frame is not None and n < start_frame:
            continue
        if end_frame is not None and n > end_frame:
            continue
        if step > 1 and ((n - (start_frame or int(frames[0].stem))) % step):
            continue

        previous = frames[max(0, i - 1)]
        nxt = frames[min(len(frames) - 1, i + 1)]
        role_paths = {"current": current, "previous": previous, "next": nxt}

        workflow = copy.deepcopy(workflow_api)
        for role, node_id in image_nodes.items():
            if role not in role_paths:
                raise ValueError(f"Unsupported image role: {role}")
            uploaded_name = client.upload_image(role_paths[role])
            _set_image(workflow, node_id, uploaded_name)
        for node_id, text in (text_overrides or {}).items():
            _set_text(workflow, node_id, text)

        prompt_id = client.queue_prompt(workflow)
        entry = client.wait_for_output(prompt_id, timeout_s=timeout_s)
        image = client.first_output_image(entry)
        dest = frames_ai / current.name
        client.download_image(image, dest)
        results.append({
            "frame": current.name,
            "prompt_id": prompt_id,
            "output": image,
            "saved_as": str(dest),
        })
    return results
