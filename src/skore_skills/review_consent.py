"""Decide whether the expensive skore-check audit may run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_ASK_CHOICES = ["review", "skip", "stop"]


def review_consent(root: Path, stem: str) -> dict[str, Any]:
    """Return the audit gate for ``stem``.

    Filesystem only: ``report.html`` and the audit digest. Does not
    open a skore Project or run checks.
    """
    cleaned = stem.strip()
    if not cleaned:
        raise ValueError("stem is required")

    report = root / "scratch" / "results" / cleaned / "report.html"
    if not report.is_file():
        return {
            "stem": cleaned,
            "action": "stop",
            "reason": "report_html_missing",
        }

    digest = root / "scratch" / "audit" / cleaned / "audit.md"
    if digest.is_file():
        return {"stem": cleaned, "action": "proceed", "reason": "digest_present"}

    return {
        "stem": cleaned,
        "action": "ask",
        "reason": "first_audit",
        "choices": list(_ASK_CHOICES),
    }


def render_review_consent(root: Path, stem: str) -> str:
    """Serialize the review-consent gate as JSON."""
    return json.dumps(review_consent(root, stem), indent=2) + "\n"
