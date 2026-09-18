from __future__ import annotations

import os

import uvicorn

# Compatibility modules read provider defaults at import time. Keep them
# aligned with the unified LuHm OS fast/deep assistance contract before any
# provider module is imported.
os.environ.setdefault("OPENAI_FAST_MODEL", "gpt-5.6-luna")
os.environ.setdefault("OPENAI_MODEL", "gpt-5.6-sol")
os.environ.setdefault("KAI_GOOGLE_FAST_TEXT_MODEL", "gemini-3.5-flash-lite")
os.environ.setdefault("KAI_GOOGLE_DEEP_TEXT_MODEL", "gemini-3.8-flash")
os.environ.setdefault("KAI_GEMINI_LIVE_API_MODEL", "gemini-3.8-live")

from ai_feed.router import ROUTER as AI_FEED_ROUTER
from api_spine import ROUTER as API_SPINE_ROUTER
from assistance import ROUTER as ASSISTANCE_ROUTER
from gateway import ROUTER as GATEWAY_ROUTER
from lum_agent.router import ROUTER as LUM_AGENT_ROUTER
from magic_chat import ROUTER as MAGIC_ROUTER
from main import APP
from remote_ai import ROUTER as REMOTE_AI_ROUTER

APP.title = "LuHm OS Unified API Cockpit"
APP.version = "4.0.0"

# /api/v1 is the canonical LuHm API spine. Remaining routers are retained as
# bounded compatibility/component planes so existing clients are not broken.
APP.include_router(API_SPINE_ROUTER)
APP.include_router(MAGIC_ROUTER)
APP.include_router(LUM_AGENT_ROUTER)
APP.include_router(AI_FEED_ROUTER)
APP.include_router(REMOTE_AI_ROUTER)
APP.include_router(ASSISTANCE_ROUTER)
APP.include_router(GATEWAY_ROUTER)


if __name__ == "__main__":
    uvicorn.run(APP, host="127.0.0.1", port=int(os.environ.get("PORT", "8797")))
