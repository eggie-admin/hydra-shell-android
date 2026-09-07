from __future__ import annotations

import os

import uvicorn

from ai_feed.router import ROUTER as AI_FEED_ROUTER
from gateway import ROUTER as GATEWAY_ROUTER
from magic_chat import ROUTER as MAGIC_ROUTER
from main import APP
from remote_ai import ROUTER as REMOTE_AI_ROUTER

APP.title = "KAI9000 jQuery Python3 Magic Cockpit"
APP.version = "3.3.0"
APP.include_router(MAGIC_ROUTER)
APP.include_router(AI_FEED_ROUTER)
APP.include_router(REMOTE_AI_ROUTER)
APP.include_router(GATEWAY_ROUTER)


if __name__ == "__main__":
    uvicorn.run(APP, host="127.0.0.1", port=int(os.environ.get("PORT", "8797")))
