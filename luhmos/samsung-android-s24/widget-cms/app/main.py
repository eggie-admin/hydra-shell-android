from __future__ import annotations

import json
from pathlib import Path

import aiosqlite
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import connect, init_db, now_iso, row_to_page
from .models import PageIn, PageOut, PagePatch
from .settings import get_settings

app = FastAPI(title="KAI Vue CMS Mutation", version="0.1.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-KAI-Admin"],
)


@app.on_event("startup")
async def startup() -> None:
    await init_db(settings.db_path)


async def db_dep() -> aiosqlite.Connection:
    async with await connect(settings.db_path) as db:
        yield db


def require_admin(x_kai_admin: str | None = Header(default=None)) -> None:
    if x_kai_admin != settings.kai_admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing KAI admin token")


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"ok": "true", "env": settings.kai_env, "mode": "donor-purged"}


@app.get("/api/pages", response_model=list[PageOut])
async def list_pages(db: aiosqlite.Connection = Depends(db_dep)) -> list[dict]:
    rows = await db.execute_fetchall("SELECT * FROM pages ORDER BY updated_at DESC")
    return [row_to_page(row) for row in rows]


@app.get("/api/pages/{slug}", response_model=PageOut)
async def get_page(slug: str, db: aiosqlite.Connection = Depends(db_dep)) -> dict:
    rows = await db.execute_fetchall("SELECT * FROM pages WHERE slug = ?", (slug,))
    if not rows:
        raise HTTPException(status_code=404, detail="Page not found")
    return row_to_page(rows[0])


@app.post("/api/pages", response_model=PageOut, dependencies=[Depends(require_admin)])
async def create_page(page: PageIn, db: aiosqlite.Connection = Depends(db_dep)) -> dict:
    ts = now_iso()
    try:
        await db.execute(
            """
            INSERT INTO pages (slug, title, body, status, metadata_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                page.slug,
                page.title,
                page.body,
                page.status,
                json.dumps(page.metadata, sort_keys=True),
                ts,
                ts,
            ),
        )
        await db.commit()
    except aiosqlite.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Slug already exists") from exc
    rows = await db.execute_fetchall("SELECT * FROM pages WHERE slug = ?", (page.slug,))
    return row_to_page(rows[0])


@app.patch("/api/pages/{slug}", response_model=PageOut, dependencies=[Depends(require_admin)])
async def update_page(slug: str, patch: PagePatch, db: aiosqlite.Connection = Depends(db_dep)) -> dict:
    current = await db.execute_fetchall("SELECT * FROM pages WHERE slug = ?", (slug,))
    if not current:
        raise HTTPException(status_code=404, detail="Page not found")

    existing = row_to_page(current[0])
    next_page = {
        "title": patch.title if patch.title is not None else existing["title"],
        "body": patch.body if patch.body is not None else existing["body"],
        "status": patch.status if patch.status is not None else existing["status"],
        "metadata": patch.metadata if patch.metadata is not None else existing["metadata"],
    }
    ts = now_iso()
    await db.execute(
        """
        UPDATE pages
        SET title = ?, body = ?, status = ?, metadata_json = ?, updated_at = ?
        WHERE slug = ?
        """,
        (
            next_page["title"],
            next_page["body"],
            next_page["status"],
            json.dumps(next_page["metadata"], sort_keys=True),
            ts,
            slug,
        ),
    )
    await db.commit()
    rows = await db.execute_fetchall("SELECT * FROM pages WHERE slug = ?", (slug,))
    return row_to_page(rows[0])


@app.delete("/api/pages/{slug}", dependencies=[Depends(require_admin)])
async def delete_page(slug: str, db: aiosqlite.Connection = Depends(db_dep)) -> dict[str, str]:
    result = await db.execute("DELETE FROM pages WHERE slug = ?", (slug,))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": slug}


# Serve the Vue build when present. API routes above win before this fallback.
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    ASSETS = DIST / "assets"
    if ASSETS.exists():
        app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def frontend(full_path: str, request: Request):
        target = DIST / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(DIST / "index.html")
