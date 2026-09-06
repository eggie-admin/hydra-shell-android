# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Any
from .db import Store

def feedback_to_candidate(store: Store, *, session_id: str, prompt: str,
                          response: str, rating: int, corrected_response: str | None,
                          note: str = "") -> dict[str, Any]:
    feedback_id = store.record_feedback(session_id, prompt, response, rating, note)
    candidate_id = None
    if corrected_response and rating < 1:
        candidate_id = store.create_learning_candidate(
            feedback_id,
            prompt,
            corrected_response,
            {
                "source": "human_feedback",
                "session_id": session_id,
                "rating": rating,
                "auto_train": False,
                "requires_human_review": True,
            },
        )
    return {"feedback_id": feedback_id, "candidate_id": candidate_id}

def approve_candidate(store: Store, example_id: int, *, reviewer: str,
                      approved: bool) -> dict[str, Any]:
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    return store.review_learning_example(
        example_id,
        approved=bool(approved),
        reviewer=reviewer,
    )

def training_export_allowed(example: dict[str, Any]) -> bool:
    return (
        example.get("state") == "approved"
        and bool(example.get("reviewer"))
        and bool(example.get("reviewed_unix"))
    )
