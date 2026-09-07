from __future__ import annotations

import asyncio
import base64
import os
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field


ROUTER = APIRouter(tags=["kai-antenna-gateway"])

GOOGLE_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
GOOGLE_TEXT_MODEL = os.environ.get("KAI_GOOGLE_TEXT_MODEL", "gemini-3.5-flash")
GEMINI_LIVE_VERTEX_MODEL = os.environ.get(
    "KAI_GEMINI_LIVE_VERTEX_MODEL", "gemini-live-2.5-flash-native-audio"
)
GEMINI_LIVE_API_MODEL = os.environ.get(
    "KAI_GEMINI_LIVE_API_MODEL", "gemini-3.1-flash-live-preview"
)


class DirectorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=16000)
    mode: str = Field(default="auto", pattern="^(auto|local|google|live)$")


class RouteRequest(BaseModel):
    kind: str = Field(default="generate", pattern="^(generate|realtime|status|media)$")
    prefer: str = Field(default="auto", pattern="^(auto|local|google)$")


class GoogleGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=16000)
    model: str | None = None


def _project_id() -> str | None:
    return (
        os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("GCP_PROJECT")
        or os.environ.get("GCP_PROJECT_ID")
        or None
    )


def _api_key() -> str | None:
    # The server may use an API key for non-GCP development, but Android never
    # receives it. On the Google VM, Vertex AI + Application Default
    # Credentials is the preferred path.
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or None


def google_auth_mode() -> str:
    requested = os.environ.get("KAI_GOOGLE_AUTH", "auto").strip().lower()
    if requested not in {"auto", "vertex", "api_key"}:
        return "invalid"
    if requested in {"auto", "vertex"} and _project_id():
        return "vertex_adc"
    if requested in {"auto", "api_key"} and _api_key():
        return "api_key"
    return "unconfigured"


def google_status() -> dict[str, Any]:
    mode = google_auth_mode()
    return {
        "configured": mode in {"vertex_adc", "api_key"},
        "auth_mode": mode,
        "transport": "google-genai HTTPS/gRPC + Live WebSocket",
        "location": GOOGLE_LOCATION if mode == "vertex_adc" else None,
        "text_model": GOOGLE_TEXT_MODEL,
        "live_model": (
            GEMINI_LIVE_VERTEX_MODEL if mode == "vertex_adc" else GEMINI_LIVE_API_MODEL
        ),
        "secrets_exposed": False,
        "android_provider_credentials": False,
    }


def _google_client():
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - deployment packaging guard
        raise HTTPException(status_code=503, detail="google-genai is not installed") from exc

    mode = google_auth_mode()
    if mode == "vertex_adc":
        return genai.Client(
            vertexai=True,
            project=_project_id(),
            location=GOOGLE_LOCATION,
        )
    if mode == "api_key":
        return genai.Client(api_key=_api_key())
    if mode == "invalid":
        raise HTTPException(status_code=500, detail="Invalid KAI_GOOGLE_AUTH configuration")
    raise HTTPException(status_code=503, detail="Google provider is not configured")


def _google_generate(prompt: str, model: str | None = None) -> dict[str, Any]:
    client = _google_client()
    resolved_model = model or GOOGLE_TEXT_MODEL
    try:
        response = client.models.generate_content(model=resolved_model, contents=prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Google generation failed without provider failover: {type(exc).__name__}",
        ) from exc

    text = getattr(response, "text", None)
    return {
        "ok": True,
        "provider": "google",
        "auth_mode": google_auth_mode(),
        "model": resolved_model,
        "text": text or "",
        "secret_material_present": False,
    }


def _route(kind: str, prefer: str) -> dict[str, Any]:
    google_ready = google_status()["configured"]

    if kind == "realtime":
        return {
            "lane": "/providers/gemini/live",
            "provider": "google" if google_ready else None,
            "ready": google_ready,
        }

    if prefer == "google":
        return {
            "lane": "/providers/google/generate",
            "provider": "google",
            "ready": google_ready,
        }

    if prefer == "local":
        return {
            "lane": "/api/antenna/ollama/chat",
            "provider": "ollama-local",
            "ready": True,
        }

    if kind == "media":
        return {"lane": "/api/jobs", "provider": "local-media", "ready": True}

    if google_ready:
        return {
            "lane": "/providers/google/generate",
            "provider": "google",
            "ready": True,
        }

    return {
        "lane": "/api/antenna/ollama/chat",
        "provider": "ollama-local",
        "ready": True,
    }


@ROUTER.get("/api/status")
def api_status() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "kai9000-remote-antenna",
        "contract": "kai9000.antenna-gateway.v1",
        "lanes": {
            "rest": "/api/*",
            "control_ws": "/ws",
            "google": "/providers/google/*",
            "gemini_live": "/providers/gemini/live",
        },
        "google": google_status(),
    }


@ROUTER.post("/api/providers/route")
def api_provider_route(req: RouteRequest) -> dict[str, Any]:
    return {"ok": True, "kind": req.kind, "prefer": req.prefer, **_route(req.kind, req.prefer)}


@ROUTER.post("/api/director")
def api_director(req: DirectorRequest) -> dict[str, Any]:
    kind = "realtime" if req.mode == "live" else "generate"
    prefer = "google" if req.mode == "google" else ("local" if req.mode == "local" else "auto")
    decision = _route(kind, prefer)
    return {
        "ok": True,
        "message_accepted": True,
        "execution": "route_only",
        "message_bytes": len(req.message.encode("utf-8")),
        **decision,
    }


@ROUTER.get("/providers/google/health")
def provider_google_health() -> dict[str, Any]:
    return {"ok": True, **google_status()}


@ROUTER.post("/providers/google/generate")
def provider_google_generate(req: GoogleGenerateRequest) -> dict[str, Any]:
    return _google_generate(req.prompt, req.model)


@ROUTER.websocket("/ws")
async def control_bus(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "hello",
            "contract": "kai9000.control-bus.v1",
            "capabilities": ["ping", "status.get", "provider.route"],
        }
    )
    try:
        while True:
            message = await websocket.receive_json()
            event_type = str(message.get("type") or "")
            if event_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif event_type == "status.get":
                await websocket.send_json({"type": "status.snapshot", "payload": api_status()})
            elif event_type == "provider.route":
                kind = str(message.get("kind") or "generate")
                prefer = str(message.get("prefer") or "auto")
                if kind not in {"generate", "realtime", "status", "media"} or prefer not in {
                    "auto",
                    "local",
                    "google",
                }:
                    await websocket.send_json(
                        {"type": "error", "code": "invalid_route_request"}
                    )
                else:
                    await websocket.send_json(
                        {"type": "provider.route", "payload": _route(kind, prefer)}
                    )
            else:
                await websocket.send_json({"type": "error", "code": "unsupported_event"})
    except WebSocketDisconnect:
        return


def _live_model() -> str:
    return GEMINI_LIVE_VERTEX_MODEL if google_auth_mode() == "vertex_adc" else GEMINI_LIVE_API_MODEL


def _normalize_live_message(message: Any) -> dict[str, Any]:
    event: dict[str, Any] = {"type": "gemini.live.event"}
    text = getattr(message, "text", None)
    if text:
        event["text"] = str(text)

    content = getattr(message, "server_content", None)
    if content is not None:
        input_tx = getattr(content, "input_transcription", None)
        output_tx = getattr(content, "output_transcription", None)
        if input_tx is not None and getattr(input_tx, "text", None):
            event["input_transcription"] = str(input_tx.text)
        if output_tx is not None and getattr(output_tx, "text", None):
            event["output_transcription"] = str(output_tx.text)
        if bool(getattr(content, "turn_complete", False)):
            event["turn_complete"] = True

        model_turn = getattr(content, "model_turn", None)
        parts = getattr(model_turn, "parts", None) if model_turn is not None else None
        normalized_parts: list[dict[str, Any]] = []
        for part in parts or []:
            if getattr(part, "text", None):
                normalized_parts.append({"type": "text", "text": str(part.text)})
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None) if inline is not None else None
            if data:
                raw = data if isinstance(data, bytes) else bytes(data)
                normalized_parts.append(
                    {
                        "type": "inline_data",
                        "mime_type": getattr(inline, "mime_type", None),
                        "data_b64": base64.b64encode(raw).decode("ascii"),
                    }
                )
        if normalized_parts:
            event["parts"] = normalized_parts

    tool_call = getattr(message, "tool_call", None)
    calls = getattr(tool_call, "function_calls", None) if tool_call is not None else None
    if calls:
        event["type"] = "provider.tool.request"
        event["execution"] = "blocked_pending_policy"
        event["calls"] = [
            {
                "name": getattr(call, "name", None),
                "id": getattr(call, "id", None),
                "args": getattr(call, "args", None),
            }
            for call in calls
        ]

    return event


async def _android_to_gemini(websocket: WebSocket, session: Any, types: Any) -> None:
    while True:
        message = await websocket.receive_json()
        event_type = str(message.get("type") or "")
        if event_type == "input.text":
            text = str(message.get("text") or "").strip()
            if not text:
                await websocket.send_json({"type": "error", "code": "empty_text"})
                continue
            await session.send_client_content(
                turns=types.Content(role="user", parts=[types.Part(text=text)])
            )
        elif event_type in {"input.audio", "input.video"}:
            encoded = str(message.get("data_b64") or "")
            if not encoded:
                await websocket.send_json({"type": "error", "code": "missing_data_b64"})
                continue
            try:
                data = base64.b64decode(encoded, validate=True)
            except Exception:
                await websocket.send_json({"type": "error", "code": "invalid_base64"})
                continue
            default_mime = "audio/pcm;rate=16000" if event_type == "input.audio" else "image/jpeg"
            blob = types.Blob(data=data, mime_type=str(message.get("mime_type") or default_mime))
            if event_type == "input.audio":
                await session.send_realtime_input(audio=blob)
            else:
                await session.send_realtime_input(video=blob)
        elif event_type == "close":
            return
        else:
            await websocket.send_json({"type": "error", "code": "unsupported_live_event"})


async def _gemini_to_android(websocket: WebSocket, session: Any) -> None:
    async for message in session.receive():
        await websocket.send_json(_normalize_live_message(message))


@ROUTER.websocket("/providers/gemini/live")
async def provider_gemini_live(websocket: WebSocket) -> None:
    await websocket.accept()
    mode = google_auth_mode()
    if mode not in {"vertex_adc", "api_key"}:
        await websocket.send_json(
            {
                "type": "provider.error",
                "code": "google_not_configured",
                "secrets_exposed": False,
            }
        )
        await websocket.close(code=1011)
        return

    try:
        from google.genai import types
    except ImportError:
        await websocket.send_json({"type": "provider.error", "code": "google_genai_missing"})
        await websocket.close(code=1011)
        return

    client = _google_client()
    modality = str(websocket.query_params.get("modality", "text")).strip().lower()
    response_modality = types.Modality.AUDIO if modality == "audio" else types.Modality.TEXT
    config = types.LiveConnectConfig(response_modalities=[response_modality])

    try:
        async with client.aio.live.connect(model=_live_model(), config=config) as session:
            await websocket.send_json(
                {
                    "type": "gemini.live.ready",
                    "auth_mode": mode,
                    "model": _live_model(),
                    "response_modality": modality,
                    "provider_credentials_on_android": False,
                }
            )
            upstream = asyncio.create_task(_android_to_gemini(websocket, session, types))
            downstream = asyncio.create_task(_gemini_to_android(websocket, session))
            done, pending = await asyncio.wait(
                {upstream, downstream}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                exc = task.exception()
                if exc and not isinstance(exc, WebSocketDisconnect):
                    raise exc
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await websocket.send_json(
                {
                    "type": "provider.error",
                    "code": "gemini_live_bridge_error",
                    "detail": type(exc).__name__,
                }
            )
            await websocket.close(code=1011)
        except Exception:
            return
