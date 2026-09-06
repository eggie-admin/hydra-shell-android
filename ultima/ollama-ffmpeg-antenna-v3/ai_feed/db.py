# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

DDL = r"""
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS schema_migrations(
  version INTEGER PRIMARY KEY,
  applied_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rss_sources(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL DEFAULT '',
  enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
  etag TEXT,
  last_modified TEXT,
  last_fetch_unix INTEGER,
  last_status INTEGER,
  last_error TEXT,
  created_unix INTEGER NOT NULL,
  updated_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rss_items(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER NOT NULL REFERENCES rss_sources(id) ON DELETE CASCADE,
  fingerprint TEXT NOT NULL UNIQUE,
  guid TEXT,
  link TEXT,
  title TEXT NOT NULL DEFAULT '',
  summary TEXT NOT NULL DEFAULT '',
  published TEXT,
  author TEXT,
  content_hash TEXT NOT NULL,
  fetched_unix INTEGER NOT NULL,
  provenance_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS memories(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  value TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_ref TEXT,
  approved INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),
  created_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  prompt TEXT NOT NULL,
  response TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK(rating BETWEEN -1 AND 1),
  note TEXT NOT NULL DEFAULT '',
  created_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_examples(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feedback_id INTEGER REFERENCES feedback(id) ON DELETE SET NULL,
  input_text TEXT NOT NULL,
  target_text TEXT NOT NULL,
  provenance_json TEXT NOT NULL DEFAULT '{}',
  state TEXT NOT NULL DEFAULT 'candidate'
    CHECK(state IN ('candidate','approved','rejected','exported')),
  reviewer TEXT,
  reviewed_unix INTEGER,
  created_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS model_versions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT NOT NULL,
  model_id TEXT NOT NULL,
  digest TEXT,
  adapter_id TEXT,
  state TEXT NOT NULL CHECK(state IN ('candidate','active','retired','rejected')),
  eval_json TEXT NOT NULL DEFAULT '{}',
  provenance_json TEXT NOT NULL DEFAULT '{}',
  created_unix INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS promotions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  model_version_id INTEGER NOT NULL REFERENCES model_versions(id),
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL,
  human_approved INTEGER NOT NULL CHECK(human_approved IN (0,1)),
  evidence_json TEXT NOT NULL DEFAULT '{}',
  created_unix INTEGER NOT NULL
);
"""

class Store:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript(DDL)
        self.db.execute(
            "INSERT OR IGNORE INTO schema_migrations(version,applied_unix) VALUES(?,?)",
            (SCHEMA_VERSION, int(time.time())),
        )
        self.fts5 = self._ensure_fts5()
        self.db.commit()

    def close(self):
        self.db.close()

    def _ensure_fts5(self) -> bool:
        try:
            self.db.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS rss_fts USING fts5("
                "item_id UNINDEXED, title, summary, tokenize='unicode61')"
            )
            return True
        except sqlite3.OperationalError:
            return False

    def integrity(self) -> str:
        return str(self.db.execute("PRAGMA integrity_check").fetchone()[0])

    def add_source(self, url: str, title: str = "") -> int:
        now = int(time.time())
        self.db.execute(
            """INSERT INTO rss_sources(url,title,created_unix,updated_unix)
               VALUES(?,?,?,?)
               ON CONFLICT(url) DO UPDATE SET
                 title=CASE WHEN excluded.title<>'' THEN excluded.title ELSE rss_sources.title END,
                 updated_unix=excluded.updated_unix""",
            (url, title[:300], now, now),
        )
        self.db.commit()
        row = self.db.execute("SELECT id FROM rss_sources WHERE url=?", (url,)).fetchone()
        return int(row["id"])

    def source(self, source_id: int) -> dict[str, Any] | None:
        row = self.db.execute("SELECT * FROM rss_sources WHERE id=?", (int(source_id),)).fetchone()
        return dict(row) if row else None

    def list_sources(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.execute(
            "SELECT * FROM rss_sources ORDER BY id"
        ).fetchall()]

    def update_fetch_state(self, source_id: int, *, etag=None, last_modified=None,
                           status=None, error=None):
        now = int(time.time())
        self.db.execute(
            """UPDATE rss_sources SET
               etag=?, last_modified=?, last_fetch_unix=?,
               last_status=?, last_error=?, updated_unix=?
               WHERE id=?""",
            (etag, last_modified, now, status, error, now, int(source_id)),
        )
        self.db.commit()

    @staticmethod
    def fingerprint(source_url: str, item: dict[str, Any]) -> str:
        stable = "\x1f".join([
            source_url,
            str(item.get("guid") or ""),
            str(item.get("link") or ""),
            str(item.get("title") or ""),
            str(item.get("published") or ""),
        ])
        return hashlib.sha256(stable.encode("utf-8")).hexdigest()

    def upsert_item(self, source_id: int, source_url: str, item: dict[str, Any]) -> tuple[int, bool]:
        fp = self.fingerprint(source_url, item)
        title = str(item.get("title") or "")[:1000]
        summary = str(item.get("summary") or "")[:12000]
        content_hash = hashlib.sha256((title + "\n" + summary).encode("utf-8")).hexdigest()
        now = int(time.time())
        before = self.db.execute("SELECT id,content_hash FROM rss_items WHERE fingerprint=?", (fp,)).fetchone()
        self.db.execute(
            """INSERT INTO rss_items(
               source_id,fingerprint,guid,link,title,summary,published,author,
               content_hash,fetched_unix,provenance_json
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(fingerprint) DO UPDATE SET
                 guid=excluded.guid, link=excluded.link, title=excluded.title,
                 summary=excluded.summary, published=excluded.published,
                 author=excluded.author, content_hash=excluded.content_hash,
                 fetched_unix=excluded.fetched_unix,
                 provenance_json=excluded.provenance_json""",
            (
                int(source_id), fp, item.get("guid"), item.get("link"),
                title, summary, item.get("published"), item.get("author"),
                content_hash, now,
                json.dumps(item.get("provenance") or {}, separators=(",",":")),
            ),
        )
        row = self.db.execute("SELECT id FROM rss_items WHERE fingerprint=?", (fp,)).fetchone()
        item_id = int(row["id"])
        if self.fts5:
            self.db.execute("DELETE FROM rss_fts WHERE item_id=?", (item_id,))
            self.db.execute(
                "INSERT INTO rss_fts(item_id,title,summary) VALUES(?,?,?)",
                (item_id, title, summary),
            )
        self.db.commit()
        changed = before is None or before["content_hash"] != content_hash
        return item_id, changed

    def search_items(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        q = str(query or "").strip()[:300]
        limit = max(1, min(int(limit), 50))
        if not q:
            return []
        if self.fts5:
            # Quote each token so FTS control syntax from user input is not executed as syntax.
            tokens = [t.replace('"', '') for t in q.split() if t.strip()]
            fts_query = " AND ".join(f'"{t}"' for t in tokens[:16])
            if not fts_query:
                return []
            rows = self.db.execute(
                """SELECT i.*, bm25(rss_fts) AS score
                   FROM rss_fts JOIN rss_items i ON i.id=rss_fts.item_id
                   WHERE rss_fts MATCH ?
                   ORDER BY score LIMIT ?""",
                (fts_query, limit),
            ).fetchall()
        else:
            like = "%" + q.replace("%", r"\%").replace("_", r"\_") + "%"
            rows = self.db.execute(
                """SELECT *, 0.0 AS score FROM rss_items
                   WHERE title LIKE ? ESCAPE '\\' OR summary LIKE ? ESCAPE '\\'
                   ORDER BY fetched_unix DESC LIMIT ?""",
                (like, like, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def record_feedback(self, session_id: str, prompt: str, response: str,
                        rating: int, note: str = "") -> int:
        rating = int(rating)
        if rating not in (-1, 0, 1):
            raise ValueError("rating must be -1, 0, or 1")
        cur = self.db.execute(
            """INSERT INTO feedback(session_id,prompt,response,rating,note,created_unix)
               VALUES(?,?,?,?,?,?)""",
            (session_id[:120], prompt[:12000], response[:12000], rating, note[:1000], int(time.time())),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def create_learning_candidate(self, feedback_id: int, input_text: str,
                                  target_text: str, provenance: dict[str, Any]) -> int:
        cur = self.db.execute(
            """INSERT INTO learning_examples(
               feedback_id,input_text,target_text,provenance_json,created_unix
               ) VALUES(?,?,?,?,?)""",
            (
                int(feedback_id), input_text[:12000], target_text[:12000],
                json.dumps(provenance, separators=(",",":")), int(time.time())
            ),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def review_learning_example(self, example_id: int, *, approved: bool, reviewer: str) -> dict[str, Any]:
        state = "approved" if approved else "rejected"
        self.db.execute(
            """UPDATE learning_examples
               SET state=?, reviewer=?, reviewed_unix=?
               WHERE id=? AND state='candidate'""",
            (state, reviewer[:120], int(time.time()), int(example_id)),
        )
        self.db.commit()
        row = self.db.execute("SELECT * FROM learning_examples WHERE id=?", (int(example_id),)).fetchone()
        if not row:
            raise ValueError("learning example not found")
        return dict(row)

    def learning_examples(self, state: str = "candidate", limit: int = 50) -> list[dict[str, Any]]:
        if state not in {"candidate","approved","rejected","exported"}:
            raise ValueError("invalid state")
        return [dict(r) for r in self.db.execute(
            "SELECT * FROM learning_examples WHERE state=? ORDER BY id DESC LIMIT ?",
            (state, max(1, min(int(limit), 200))),
        ).fetchall()]
