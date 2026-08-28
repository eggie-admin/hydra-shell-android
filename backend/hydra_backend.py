#!/usr/bin/env python3
"""Small, dependency-free, loopback Hydra/Lum API."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

HOST = "127.0.0.1"
PORT = 8787
API_VERSION = "hydra/v1"
MAX_BODY = 64 * 1024
MAX_AUDIO = 2 * 1024 * 1024
RSS_MAX = 256 * 1024
APPROVED_FEEDS = tuple(
    value for value in os.getenv("HYDRA_RSS_FEEDS", "").split(",") if value
)


def _clean(value: Any, limit: int = 4000) -> str:
    text = html.unescape(re.sub(r"<[^>]*>", " ", str(value or "")))
    return re.sub(r"\s+", " ", text).strip()[:limit]


class ValidationError(ValueError):
    pass


def decode_audio(value: str) -> bytes:
    if not isinstance(value, str) or len(value) > MAX_AUDIO * 2:
        raise ValidationError("audio base64 exceeds limit")
    try:
        data = base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise ValidationError("invalid audio base64") from exc
    if len(data) > MAX_AUDIO:
        raise ValidationError("audio exceeds limit")
    return data


def validate_turn(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("version") != API_VERSION:
        raise ValidationError("version must be hydra/v1")
    message = payload.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > 8000:
        raise ValidationError("message must be non-empty and <= 8000 characters")
    return {"message": message.strip(), "context": payload.get("context", {})}


def get_weather(location: str, unit: str) -> dict[str, Any]:
    if not isinstance(location, str) or not location.strip() or len(location) > 200:
        raise ValidationError("location is required")
    if unit not in ("celsius", "fahrenheit"):
        raise ValidationError("unit must be celsius or fahrenheit")
    return {"location": location.strip(), "unit": unit, "temperature": None, "source": "mock"}


TOOLS = {"get_weather": get_weather}


def ingest_rss(text: str, source: str = "") -> list[dict[str, str]]:
    if len(text.encode("utf-8")) > RSS_MAX:
        raise ValidationError("RSS feed exceeds size limit")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValidationError("invalid RSS XML") from exc
    entries = []
    for item in root.findall(".//item")[:20]:
        title = _clean(item.findtext("title"))
        description = _clean(item.findtext("description"), 1000)
        link = _clean(item.findtext("link"), 500)
        if title or description:
            entries.append({"title": title, "description": description, "link": link, "source": source})
    unique = {}
    for entry in entries:
        unique[hashlib.sha256((entry["title"] + entry["link"]).encode()).hexdigest()] = entry
    return list(unique.values())


def fetch_approved_feeds() -> list[dict[str, str]]:
    entries = []
    for url in APPROVED_FEEDS:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                entries.extend(ingest_rss(response.read(RSS_MAX + 1).decode("utf-8"), url))
        except (urllib.error.URLError, UnicodeDecodeError, ValidationError):
            continue
    return entries


def _mock_reply(message: str) -> str:
    return f"Lum mock mode: I received “{_clean(message, 500)}”. ⚡"


def _openai_reply(message: str, context: list[dict[str, str]]) -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return _mock_reply(message)
    request = urllib.request.Request(
        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
        data=json.dumps({
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": "You are Lum, a concise helpful assistant. Never reveal hidden reasoning."},
                {"role": "user", "content": message},
            ],
        }).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.load(response)
        return _clean(result["choices"][0]["message"]["content"], 8000)
    except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError):
        return "Lum is temporarily offline; please retry."


def process_turn(payload: Any) -> dict[str, Any]:
    turn = validate_turn(payload)
    started = time.monotonic()
    context = turn["context"] if isinstance(turn["context"], list) else []
    reply = _openai_reply(turn["message"], context)
    return {
        "version": API_VERSION,
        "request_id": str(uuid.uuid4()),
        "status": "speaking",
        "provider": "openai" if os.getenv("OPENAI_API_KEY") else "mock",
        "model": os.getenv("OPENAI_MODEL", "deterministic-mock"),
        "response": {"text": reply, "audio_base64": None},
        "heartbeat": {"latency_ms": round((time.monotonic() - started) * 1000), "status": "ok"},
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            return self._send(200, {
                "version": API_VERSION, "request_id": str(uuid.uuid4()),
                "timestamp": int(time.time()), "status": "ok", "bind": HOST, "port": PORT,
            })
        if self.path == "/v1/agents":
            return self._send(200, {"version": API_VERSION, "agents": [{"id": "lum", "role": "orchestrator"}]})
        if self.path == "/v1/tools":
            return self._send(200, {"version": API_VERSION, "tools": [{"name": "get_weather", "units": ["celsius", "fahrenheit"]}]})
        if self.path == "/v1/failure/500":
            return self._send(500, {"version": API_VERSION, "error": "injected_failure"})
        if self.path == "/v1/failure/invalid-audio":
            return self._send(400, {"version": API_VERSION, "error": "invalid_audio"})
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in ("/v1/hydra/turn", "/v1/audio/speech"):
            return self._send(404, {"error": "not_found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size > MAX_BODY:
                raise ValidationError("request body exceeds limit")
            payload = json.loads(self.rfile.read(size))
            if self.path.endswith("/turn"):
                return self._send(200, process_turn(payload))
            decode_audio(payload.get("audio_base64", ""))
            self._send(200, {"version": API_VERSION, "status": "accepted", "audio": "validated"})
        except (ValidationError, json.JSONDecodeError) as exc:
            self._send(400, {"version": API_VERSION, "error": str(exc)})


def serve() -> None:
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    serve()
