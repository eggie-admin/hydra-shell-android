#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path


def detect_ext(data: bytes) -> str:
    if data.startswith(b"RIFF"):
        return ".wav"
    if data.startswith(b"fLaC"):
        return ".flac"
    if data.startswith(b"OggS"):
        return ".ogg"
    if data.startswith(b"ID3") or (len(data) > 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return ".mp3"
    return ".bin"


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate one Japanese LuHm TTS cache entry through Hugging Face InferenceClient.")
    ap.add_argument("--ja", required=True, help="Japanese text to synthesize")
    ap.add_argument("--en", default="", help="English subtitle metadata")
    ap.add_argument("--emotion", default="neutral")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    text = args.ja.strip()
    if not text or len(text) > 1000:
        raise SystemExit("Japanese text must be 1..1000 characters")

    token = os.environ.get("HF_TOKEN")
    model = os.environ.get("LUHM_HF_TTS_MODEL")
    provider = os.environ.get("LUHM_HF_PROVIDER", "auto")
    if not token:
        raise SystemExit("HF_TOKEN is required in the private Termux environment")
    if not model:
        raise SystemExit("LUHM_HF_TTS_MODEL is required; choose a Japanese TTS model whose license fits your private use")

    root = Path(os.environ.get("LUHM_PRIVATE_ASSET_ROOT", "~/luhm-private/assets")).expanduser().resolve()
    cache = root / "voice-cache"
    cache.mkdir(parents=True, exist_ok=True)
    ttl = int(os.environ.get("LUHM_TTS_TTL_SECONDS", "604800"))
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    meta_path = cache / f"{key}.json"

    if meta_path.exists() and not args.force:
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if int(meta.get("expires_at", 0)) > int(time.time()):
                print(f"cache hit: {meta_path}")
                return
        except Exception:
            pass

    from huggingface_hub import InferenceClient

    client = InferenceClient(provider=provider, api_key=token)
    audio = client.text_to_speech(text=text, model=model)
    if not isinstance(audio, (bytes, bytearray)) or not audio:
        raise SystemExit("Hugging Face returned no audio bytes")

    ext = detect_ext(bytes(audio))
    audio_path = cache / f"{key}{ext}"
    audio_path.write_bytes(bytes(audio))
    now = int(time.time())
    metadata = {
        "schema": "luhm.tts-cache-entry.v1",
        "key": key,
        "ja": text,
        "en": args.en,
        "emotion": args.emotion,
        "provider": f"huggingface:{model}",
        "created_at": now,
        "expires_at": now + max(60, ttl),
        "audio_path": f"voice-cache/{audio_path.name}",
        "private_only": True,
        "redistribution": False
    }
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(meta_path)
    print(audio_path)


if __name__ == "__main__":
    main()
