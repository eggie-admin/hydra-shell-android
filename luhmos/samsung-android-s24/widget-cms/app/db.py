from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

SEED_PAGES = [
    {
        "slug": "home",
        "title": "KAI CMS Home",
        "body": "Welcome to the donor-purged KAI-owned CMS mutation.",
        "status": "published",
        "metadata": {"lane": "cms", "owner": "kai"},
    },
    {
        "slug": "source-of-truth",
        "title": "Source of Truth",
        "body": "Chrome Dev and Chrome Canary are behavior/test harnesses only. APK builds stay KAI-owned.",
        "status": "published",
        "metadata": {"sealed": True},
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def connect(db_path: Path) -> aiosqlite.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    return db


async def init_db(db_path: Path) -> None:
    async with await connect(db_path) as db:
        await db.executescript(SCHEMA)
        count = await db.execute_fetchall("SELECT COUNT(*) AS n FROM pages")
        if count and count[0]["n"] == 0:
            ts = now_iso()
            for page in SEED_PAGES:
                await db.execute(
                    """
                    INSERT INTO pages (slug, title, body, status, metadata_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        page["slug"],
                        page["title"],
                        page["body"],
                        page["status"],
                        json.dumps(page["metadata"], sort_keys=True),
                        ts,
                        ts,
                    ),
                )
        await db.commit()


def row_to_page(row: aiosqlite.Row) -> dict[str, Any]:
    data = dict(row)
    data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
    return data
