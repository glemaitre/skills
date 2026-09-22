"""Extract the short approval context carried by a design note."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HEADING = re.compile(r"^##\s+(?P<name>.+?)\s*$", re.MULTILINE)
_BULLET = re.compile(r"^\s*-\s+(?P<body>.+?)\s*$")
_EMPTY_CONTEXT: dict[str, Any] = {
    "note": "",
    "question": "",
    "source": "",
    "files_touched": "",
    "change": "",
    "risks": [],
}


def _sections(text: str) -> dict[str, str]:
    body = _COMMENT.sub("", text)
    matches = list(_HEADING.finditer(body))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        stop = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[match.group("name").lower()] = body[start:stop]
    return result


def _section(sections: dict[str, str], prefix: str) -> str:
    for name, body in sections.items():
        if name.startswith(prefix):
            return body
    return ""


def _clean(value: str) -> str:
    text = value.strip()
    if text.startswith("<") and text.endswith(">"):
        return ""
    return text


def _items(section: str) -> list[str]:
    """Return the section bullets with wrapped continuation lines folded in."""
    items: list[str] = []
    current: list[str] | None = None
    for line in section.splitlines():
        bullet = _BULLET.match(line)
        if bullet is not None:
            if current is not None:
                items.append(" ".join(current))
            current = [bullet.group("body").strip()]
            continue
        stripped = line.strip()
        if current is None:
            continue
        if not stripped or stripped.startswith("#"):
            items.append(" ".join(current))
            current = None
            continue
        current.append(stripped)
    if current is not None:
        items.append(" ".join(current))
    return items


def _field(items: list[str], label: str) -> str:
    pattern = re.compile(rf"^\*\*{re.escape(label)}[^:]*:\*\*\s*(?P<value>.*)$")
    for index, item in enumerate(items):
        match = pattern.match(item)
        if match is None:
            continue
        value = _clean(match.group("value"))
        if value:
            return value
        nested = items[index + 1] if index + 1 < len(items) else ""
        return "" if nested.startswith("**") else _clean(nested)
    return ""


def _question(section: str) -> str:
    for line in section.splitlines():
        text = _clean(line.strip().removeprefix("- "))
        if text:
            return text
    return ""


def design_context(root: Path, stem: str) -> dict[str, Any]:
    """Return the facts a design-approval gate must state inline.

    Parameters
    ----------
    root : pathlib.Path
        Workspace root holding ``journal/``.
    stem : str
        Experiment stem, e.g. ``01_dummy``.

    Returns
    -------
    dict
        ``note``, ``question``, ``source``, ``files_touched``, ``change``, and
        ``risks``. A field the note leaves as a template placeholder comes back
        empty so the gate reports the note is not ready instead of inventing it.
    """
    path = root / "journal" / f"{stem}.md"
    if not path.is_file():
        return dict(_EMPTY_CONTEXT)

    sections = _sections(path.read_text(encoding="utf-8"))
    method = _items(_section(sections, "method"))
    risks = [_clean(item) for item in _items(_section(sections, "risks"))]
    return {
        "note": f"journal/{stem}.md",
        "question": _question(_section(sections, "question")),
        "source": _field(_items(_section(sections, "motivation")), "Source(s)"),
        "files_touched": _field(method, "Files touched"),
        "change": _field(method, "Change versus"),
        "risks": [risk for risk in risks if risk][:2],
    }
