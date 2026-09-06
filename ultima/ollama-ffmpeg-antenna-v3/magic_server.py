from __future__ import annotations

import os

import uvicorn

from magic_chat import ROUTER
from main import APP

APP.include_router(ROUTER)


if __name__ == "__main__":
    uvicorn.run(APP, host="127.0.0.1", port=int(os.environ.get("PORT", "8797")))
