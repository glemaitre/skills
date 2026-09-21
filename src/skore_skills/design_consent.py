"""Decide whether a design note is approved before implementation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_STATE = re.compile(r"^\s*-\s*\*\*State:\*\*\s*(.+?)\s*$", re.MULTILINE)
_PROCEED_STATES = frozenset({"approved", "running", "done"})
_ASK_CHOICES = ["approve", "modify", "stop"]


def _state(text: str) -> str:
    match = _STATE.search(text)
    if match is None:
        return ""
    token = match.group(1).strip().strip("`")
    parts = token.split()
    if not parts:
        return ""
    return parts[0].lower().rstrip(".,;:")


def design_consent(root: Path, stem: str) -> dict[str, Any]:
    """Return the design-approval gate for ``stem``.

    Filesystem only: ``journal/<stem>.md`` Status. Does not run pytest.
    """
    cleaned = stem.strip()
    if not cleaned:
        raise ValueError("stem is required")

    path = root / "journal" / f"{cleaned}.md"
    if not path.is_file():
        return {"stem": cleaned, "action": "stop", "reason": "missing_design"}

    state = _state(path.read_text(encoding="utf-8"))
    if state == "abandoned":
        return {"stem": cleaned, "action": "stop", "reason": "abandoned"}
    if state in _PROCEED_STATES:
        return {"stem": cleaned, "action": "proceed", "reason": state}

    return {
        "stem": cleaned,
        "action": "ask",
        "reason": "first_approval",
        "choices": list(_ASK_CHOICES),
    }


def render_design_consent(root: Path, stem: str) -> str:
    """Serialize the design-consent gate as JSON."""
    return json.dumps(design_consent(root, stem), indent=2) + "\n"
