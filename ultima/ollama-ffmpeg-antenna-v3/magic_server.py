from __future__ import annotations

import os

import uvicorn

# Compatibility modules still read OPENAI_MODEL at import time. Keep their
# runtime default aligned with the unified LuHm OS fast/deep model contract.
os.environ.setdefault("OPENAI_FAST_MODEL", "gpt-5.6-luna")
os.environ.setdefault("OPENAI_MODEL", "gpt-5.6-sol")

from ai_feed.router import ROUTER as AI_FEED_ROUTER
from assistance import ROUTER as ASSISTANCE_ROUTER
from gateway import ROUTER as GATEWAY_ROUTER
from lum_agent.router import ROUTER as LUM_AGENT_ROUTER
from magic_chat import ROUTER as MAGIC_ROUTER
from main import APP
from remote_ai import ROUTER as REMOTE_AI_ROUTER

APP.title = "LuHm OS Remote Assistance Cockpit"
APP.version = "3.5.0"
APP.include_router(MAGIC_ROUTER)
APP.include_router(LUM_AGENT_ROUTER)
APP.include_router(AI_FEED_ROUTER)
APP.include_router(REMOTE_AI_ROUTER)
APP.include_router(ASSISTANCE_ROUTER)
APP.include_router(GATEWAY_ROUTER)


if __name__ == "__main__":
    uvicorn.run(APP, host="127.0.0.1", port=int(os.environ.get("PORT", "8797")))
