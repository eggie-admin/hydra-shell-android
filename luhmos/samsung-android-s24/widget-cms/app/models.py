from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


PageStatus = Literal["draft", "published", "archived"]


class PageIn(BaseModel):
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,80}$")
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=100_000)
    status: PageStatus = "draft"
    metadata: dict[str, Any] = Field(default_factory=dict)


class PagePatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    body: str | None = Field(default=None, min_length=1, max_length=100_000)
    status: PageStatus | None = None
    metadata: dict[str, Any] | None = None


class PageOut(PageIn):
    id: int
    created_at: str
    updated_at: str
