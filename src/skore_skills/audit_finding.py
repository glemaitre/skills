"""Parse an audit digest into the normalized G-AUDIT-FINDING string."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

UNAVAILABLE = "n/a — audit digest unavailable"
CLEAN = "0 issues, 0 tips — automated checks surfaced no actionable finding"
_CODE = re.compile(r"^\s*-\s*\[([A-Za-z0-9]+)\]")
_METRIC_LINE = re.compile(
    r"^\s*(mae|rmse|r2|roc_auc|roc-auc|accuracy|log_loss|log-loss)\s+"
    r"([+-]?(?:\d+\.\d+|\d+)(?:[eE][+-]?\d+)?)",
    re.IGNORECASE,
)


def _section_lines(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if line.strip().rstrip(":") == heading:
            start = index + 1
            break
    if start is None:
        return []
    collected: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("- "):
            collected.append(line)
            continue
        if stripped == "" and collected:
            continue
        if collected:
            break
    return collected


def _codes(text: str, heading: str) -> list[str]:
    codes: list[str] = []
    for line in _section_lines(text, heading):
        match = _CODE.match(line)
        if match:
            codes.append(match.group(1))
    return codes


def _headline_metric(text: str) -> str | None:
    index = text.find("## Metrics summary")
    block = text[index:] if index != -1 else text
    for line in block.splitlines():
        match = _METRIC_LINE.match(line)
        if match is None:
            continue
        name = match.group(1).lower().replace("-", "_")
        value = match.group(2)
        labels = {
            "mae": "MAE",
            "rmse": "RMSE",
            "r2": "R²",
            "roc_auc": "ROC-AUC",
            "accuracy": "accuracy",
            "log_loss": "log-loss",
        }
        return f"{labels[name]} {value}"
    return None


def format_finding(issues: list[str], tips: list[str], metric: str | None) -> str:
    """Return the one-line G-AUDIT-FINDING string."""
    if not issues and not tips:
        text = CLEAN
    else:
        parts = [f"{code} (issue)" for code in issues]
        parts.extend(f"{code} (tip)" for code in tips)
        text = f"{len(issues)} issue(s), {len(tips)} tip(s) — " + ", ".join(parts)
    if metric:
        text = f"{text}; {metric}"
    return text


def audit_finding(path: Path) -> dict[str, Any]:
    """Return the finding payload for a digest path."""
    if not path.is_file():
        return {
            "action": "stop",
            "reason": "digest_missing",
            "finding": UNAVAILABLE,
            "issues": [],
            "tips": [],
        }
    text = path.read_text(encoding="utf-8")
    if "**error:**" in text and "Checks summary" not in text:
        return {
            "action": "stop",
            "reason": "digest_error",
            "finding": UNAVAILABLE,
            "issues": [],
            "tips": [],
        }
    issues = _codes(text, "Issues")
    tips = _codes(text, "Tips")
    metric = _headline_metric(text)
    return {
        "action": "proceed",
        "reason": "parsed",
        "finding": format_finding(issues, tips, metric),
        "issues": issues,
        "tips": tips,
    }


def default_digest(root: Path, stem: str) -> Path:
    """Return ``scratch/audit/<stem>/audit.md``."""
    return root / "scratch" / "audit" / stem / "audit.md"


def render_audit_finding(payload: dict[str, Any]) -> str:
    """Serialize an audit-finding payload."""
    return json.dumps(payload, indent=2) + "\n"
