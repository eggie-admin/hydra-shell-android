# SPDX-License-Identifier: MIT
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .agent import chat
from .db import Store
from .feeds import FeedError, fetch_feed, parse_feed_bytes, validate_feed_url
from .learning import approve_candidate, feedback_to_candidate

ROUTER = APIRouter(prefix="/api/ai", tags=["ai-feed"])
STATE_ROOT = Path(os.environ.get(
    "KAI_AI_STATE",
    str(Path(__file__).resolve().parents[1] / "data" / "ai")
)).resolve()
STATE_ROOT.mkdir(parents=True, exist_ok=True)
STORE = Store(STATE_ROOT / "kai_ai.sqlite3")

class SourceRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)
    title: str = Field(default="", max_length=300)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4096)
    search: str | None = Field(default=None, max_length=300)
    model: str | None = Field(default=None, max_length=160)

class FeedbackRequest(BaseModel):
    session_id: str = Field(default="default", max_length=120)
    prompt: str = Field(min_length=1, max_length=12000)
    response: str = Field(min_length=1, max_length=12000)
    rating: int = Field(ge=-1, le=1)
    corrected_response: str | None = Field(default=None, max_length=12000)
    note: str = Field(default="", max_length=1000)

class ReviewRequest(BaseModel):
    approved: bool
    reviewer: str = Field(min_length=1, max_length=120)

@ROUTER.get("/health")
def health():
    return {
        "ok": STORE.integrity() == "ok",
        "schema": "kai9000.ai-feed.v1",
        "sqlite_integrity": STORE.integrity(),
        "fts5": STORE.fts5,
        "learning": "review-gated",
        "auto_training": False,
        "runtime_owner": "ordinary-termux",
    }

@ROUTER.get("/rss/sources")
def list_sources():
    return {"ok": True, "sources": STORE.list_sources()}

@ROUTER.post("/rss/sources")
def add_source(req: SourceRequest):
    try:
        url = validate_feed_url(req.url)
    except FeedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    source_id = STORE.add_source(url, req.title)
    return {"ok": True, "source_id": source_id, "url": url}

@ROUTER.post("/rss/sources/{source_id}/refresh")
def refresh_source(source_id: int):
    source = STORE.source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="source not found")
    try:
        result = fetch_feed(
            source["url"],
            etag=source.get("etag"),
            last_modified=source.get("last_modified"),
        )
        if result["status"] == 304:
            STORE.update_fetch_state(
                source_id,
                etag=result.get("etag"),
                last_modified=result.get("last_modified"),
                status=304,
                error=None,
            )
            return {"ok": True, "status": 304, "items": 0, "changed": 0}

        parsed = parse_feed_bytes(result["body"], result["url"])
        if parsed["title"]:
            STORE.add_source(source["url"], parsed["title"])
        changed = 0
        for item in parsed["items"]:
            _, was_changed = STORE.upsert_item(source_id, source["url"], item)
            changed += int(was_changed)
        STORE.update_fetch_state(
            source_id,
            etag=result.get("etag"),
            last_modified=result.get("last_modified"),
            status=result["status"],
            error=None,
        )
        return {
            "ok": True,
            "status": result["status"],
            "items": len(parsed["items"]),
            "changed": changed,
        }
    except FeedError as exc:
        STORE.update_fetch_state(source_id, status=None, error=str(exc)[:1000])
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@ROUTER.get("/rss/search")
def search(q: str, limit: int = 10):
    return {"ok": True, "items": STORE.search_items(q, limit)}

@ROUTER.post("/chat")
def agent_chat(req: ChatRequest):
    rows = STORE.search_items(req.search, 8) if req.search else []
    try:
        return chat(req.message, retrieved=rows, model=req.model)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)[:500]) from exc

@ROUTER.post("/learning/feedback")
def learning_feedback(req: FeedbackRequest):
    return feedback_to_candidate(
        STORE,
        session_id=req.session_id,
        prompt=req.prompt,
        response=req.response,
        rating=req.rating,
        corrected_response=req.corrected_response,
        note=req.note,
    )

@ROUTER.get("/learning/examples")
def learning_examples(state: str = "candidate", limit: int = 50):
    try:
        return {"ok": True, "examples": STORE.learning_examples(state, limit)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@ROUTER.post("/learning/examples/{example_id}/review")
def review_example(example_id: int, req: ReviewRequest):
    try:
        return {
            "ok": True,
            "example": approve_candidate(
                STORE, example_id, reviewer=req.reviewer, approved=req.approved
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
