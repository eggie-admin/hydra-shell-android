from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import httpx

PASS_ORDER = (
    "01_INPUT_GATE",
    "02_INGEST",
    "03_NORMALIZE_JSON",
    "04_DEDUPE",
    "05_RELEVANCE_RANK",
    "06_PROVENANCE_GATE",
    "07_CONTEXT_BUDGET",
    "08_BOSS_ROUTE",
    "09_REMOTE_AI",
    "10_FINAL_GUARD",
)

MAX_FEED_BYTES = max(
    32_768,
    min(int(os.environ.get("LUM_RSS_MAX_BYTES", "1048576")), 4_194_304),
)
MAX_CONTEXT_CHARS = max(
    2_000,
    min(int(os.environ.get("LUM_MESH_MAX_CONTEXT_CHARS", "12000")), 50_000),
)
RSS_TIMEOUT = max(
    3.0,
    min(float(os.environ.get("LUM_RSS_TIMEOUT", "12")), 30.0),
)


def _clean_text(value: Any, *, limit: int = 2000) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def _allowed_rss_hosts() -> set[str]:
    raw = os.environ.get("LUM_RSS_ALLOWED_HOSTS", "")
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _fetch_rss(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("RSS URL must use https and include a hostname")
    allowed = _allowed_rss_hosts()
    if not allowed or parsed.hostname.lower() not in allowed:
        raise ValueError("RSS host is not allowlisted by LUM_RSS_ALLOWED_HOSTS")
    response = httpx.get(
        url,
        timeout=RSS_TIMEOUT,
        follow_redirects=False,
        headers={"User-Agent": "LuHmOS-LumMesh/1.0"},
    )
    response.raise_for_status()
    body = response.content
    if len(body) > MAX_FEED_BYTES:
        raise ValueError("RSS payload exceeds configured byte budget")
    return body.decode(response.encoding or "utf-8", errors="replace")


def _first_text(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in node.iter():
        local = child.tag.rsplit("}", 1)[-1].lower()
        if local in names and child.text:
            value = _clean_text(child.text)
            if value:
                return value
    return ""


def _entry_link(node: ET.Element) -> str:
    for child in node.iter():
        local = child.tag.rsplit("}", 1)[-1].lower()
        if local != "link":
            continue
        href = _clean_text(child.attrib.get("href", ""), limit=1000)
        if href:
            return href
        if child.text:
            value = _clean_text(child.text, limit=1000)
            if value:
                return value
    return ""


def _parse_rss(xml_text: str, source_url: str | None = None) -> list[dict[str, Any]]:
    if len(xml_text.encode("utf-8", errors="ignore")) > MAX_FEED_BYTES:
        raise ValueError("RSS payload exceeds configured byte budget")
    root = ET.fromstring(xml_text)
    entries = [
        node
        for node in root.iter()
        if node.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}
    ]
    out: list[dict[str, Any]] = []
    for node in entries:
        out.append(
            {
                "title": _first_text(node, ("title",)),
                "link": _entry_link(node),
                "summary": _first_text(node, ("description", "summary", "content")),
                "published": _first_text(node, ("pubdate", "published", "updated", "date")),
                "source": source_url or "inline_rss",
            }
        )
    return out


def _stable_id(item: dict[str, Any]) -> str:
    basis = "\n".join(
        [
            _clean_text(item.get("link"), limit=1000),
            _clean_text(item.get("title"), limit=500),
            _clean_text(item.get("published"), limit=200),
        ]
    )
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:20]


def _normalize_item(item: dict[str, Any], source: str) -> dict[str, Any]:
    normalized = {
        "title": _clean_text(item.get("title"), limit=500),
        "link": _clean_text(item.get("link"), limit=1000),
        "summary": _clean_text(item.get("summary") or item.get("description"), limit=2400),
        "published": _clean_text(item.get("published"), limit=200),
        "source": _clean_text(item.get("source") or source, limit=1000),
    }
    normalized["id"] = _stable_id(normalized)
    return normalized


def _keywords(query: str) -> list[str]:
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9_+-]{3,}", query)
        if token.lower() not in {"with", "from", "that", "this", "have", "into"}
    ][:24]


def _score(item: dict[str, Any], terms: list[str]) -> int:
    if not terms:
        return 1
    haystack = f"{item['title']} {item['summary']}".lower()
    title = item["title"].lower()
    return sum(3 if term in title else 1 for term in terms if term in haystack)


def _build_boss_prompt(query: str, selected: list[dict[str, Any]], route: str) -> str:
    evidence = [
        {
            "id": item["id"],
            "title": item["title"],
            "link": item["link"],
            "published": item["published"],
            "source": item["source"],
            "summary": item["summary"],
            "score": item.get("score", 0),
        }
        for item in selected
    ]
    packet = {
        "schema": "luhmos.lum-mesh.rss-evidence.v1",
        "boss": "Lum",
        "route": route,
        "query": query,
        "evidence": evidence,
        "rules": [
            "Use only the supplied evidence for feed-derived factual claims.",
            "Do not claim tools or mutations executed unless evidence explicitly proves it.",
            "Identify uncertainty instead of filling gaps.",
            "Return a concise synthesis optimized for Professor review.",
        ],
    }
    return (
        "LUM BOSS TASK\n"
        "Synthesize this normalized RSS/JSON evidence packet. This is advisory analysis only.\n"
        + json.dumps(packet, ensure_ascii=False, separators=(",", ":"))
    )


def run_ten_pass_mesh(
    *,
    query: str,
    invoke_boss: Callable[[str, str], dict[str, Any]],
    rss_url: str | None = None,
    rss_xml: str | None = None,
    items: list[dict[str, Any]] | None = None,
    max_items: int = 12,
    deep: bool = False,
) -> dict[str, Any]:
    """Run ten bounded logic passes while making at most one remote model call.

    The ten passes are pipeline logic, not ten paid AI invocations. That keeps the
    mesh sharp: deterministic helpers prepare evidence; Lum is the single boss.
    """

    max_items = min(max(int(max_items), 1), 25)
    trace: list[dict[str, Any]] = []
    state: dict[str, Any] = {
        "query": _clean_text(query, limit=4000),
        "source_kind": None,
        "raw_items": [],
        "normalized": [],
        "selected": [],
        "route": "fast",
        "boss_result": None,
    }

    for name in PASS_ORDER:
        if name == "01_INPUT_GATE":
            source_count = sum(bool(value) for value in (rss_url, rss_xml, items))
            if source_count != 1:
                raise ValueError("Provide exactly one of rss_url, rss_xml, or items")
            if not state["query"]:
                raise ValueError("query is required")
            state["source_kind"] = (
                "rss_url" if rss_url else "rss_xml" if rss_xml else "json_items"
            )

        elif name == "02_INGEST":
            if rss_url:
                xml_text = _fetch_rss(rss_url)
                state["raw_items"] = _parse_rss(xml_text, rss_url)
            elif rss_xml:
                state["raw_items"] = _parse_rss(rss_xml)
            else:
                state["raw_items"] = [dict(item) for item in (items or [])]
            if not state["raw_items"]:
                raise ValueError("No feed items were ingested")

        elif name == "03_NORMALIZE_JSON":
            source = rss_url or state["source_kind"] or "inline"
            state["normalized"] = [
                _normalize_item(item, source) for item in state["raw_items"]
            ]

        elif name == "04_DEDUPE":
            seen: set[str] = set()
            deduped: list[dict[str, Any]] = []
            for item in state["normalized"]:
                key = item["link"] or item["id"]
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(item)
            state["normalized"] = deduped

        elif name == "05_RELEVANCE_RANK":
            terms = _keywords(state["query"])
            for item in state["normalized"]:
                item["score"] = _score(item, terms)
            state["normalized"].sort(
                key=lambda item: (item.get("score", 0), bool(item.get("published"))),
                reverse=True,
            )

        elif name == "06_PROVENANCE_GATE":
            state["normalized"] = [
                item
                for item in state["normalized"]
                if item["title"] and (item["link"] or item["source"])
            ]
            if not state["normalized"]:
                raise ValueError("No feed items survived the provenance gate")

        elif name == "07_CONTEXT_BUDGET":
            selected: list[dict[str, Any]] = []
            chars = 0
            for item in state["normalized"]:
                if len(selected) >= max_items:
                    break
                cost = len(item["title"]) + len(item["summary"]) + len(item["link"])
                if selected and chars + cost > MAX_CONTEXT_CHARS:
                    break
                selected.append(item)
                chars += cost
            state["selected"] = selected
            state["context_chars"] = chars

        elif name == "08_BOSS_ROUTE":
            state["route"] = "deep" if deep or len(state["selected"]) > 12 else "fast"

        elif name == "09_REMOTE_AI":
            prompt = _build_boss_prompt(state["query"], state["selected"], state["route"])
            state["boss_result"] = invoke_boss(prompt, state["route"])

        elif name == "10_FINAL_GUARD":
            result = state["boss_result"]
            if not isinstance(result, dict) or not result.get("ok"):
                raise ValueError("Lum boss did not return a successful structured result")
            if result.get("execution") not in {"AGENT_COMPLETED", "NOT_EXECUTED"}:
                raise ValueError("Unexpected Lum execution state")
            assistant = _clean_text(result.get("assistant"), limit=12000)
            if not assistant:
                raise ValueError("Lum boss returned no assistant text")
            state["assistant"] = assistant

        trace.append(
            {
                "pass": name,
                "status": "GREEN",
                "items": len(state.get("normalized", [])),
                "selected": len(state.get("selected", [])),
                "route": state.get("route"),
            }
        )

    boss_result = dict(state["boss_result"] or {})
    return {
        "ok": True,
        "schema": "luhmos.lum-agent-mesh.result.v1",
        "pipeline": "RSS_XML_OR_JSON -> NORMALIZED_JSON -> LUM_BOSS",
        "passes": trace,
        "pass_count": len(trace),
        "remote_model_calls": 0 if boss_result.get("execution") == "NOT_EXECUTED" else 1,
        "route": state["route"],
        "source_kind": state["source_kind"],
        "ingested_count": len(state["raw_items"]),
        "normalized_count": len(state["normalized"]),
        "selected_count": len(state["selected"]),
        "evidence": state["selected"],
        "assistant": state["assistant"],
        "boss": {
            "agent": boss_result.get("agent"),
            "model": boss_result.get("model"),
            "mode": boss_result.get("mode"),
            "execution": boss_result.get("execution"),
        },
        "authority": {
            "self_approval": False,
            "mutation_authority": False,
            "public_publish": False,
        },
    }
