"""Filesystem gates for evaluate / audit close and the persisted locator."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

MISSING_LOCATOR = "n/a — backend did not expose a locator"
_PERSISTED = re.compile(
    r"^# %% \[markdown\]\s*\n# ## Persisted report\s*\n#\s*\n# (.+)$",
    re.MULTILINE,
)


def _results_dir(root: Path, stem: str) -> Path:
    return root / "scratch" / "results" / stem


def _exists(path: Path) -> bool:
    return path.is_file()


def loop_artifacts(root: Path, stem: str) -> dict[str, Any]:
    """Return which close step is due for ``stem``."""
    cleaned = stem.strip()
    if not cleaned:
        raise ValueError("stem is required")
    results = _results_dir(root, cleaned)
    smoke = root / "tests" / "smoke" / f"test_{cleaned}.py"
    experiment = root / "experiments" / f"{cleaned}.py"
    digest = root / "scratch" / "audit" / cleaned / "audit.md"
    report_html = results / "report.html"
    files = {
        "smoke": _exists(smoke),
        "experiment": _exists(experiment),
        "report_html": _exists(report_html),
        "report_txt": _exists(results / "report.txt"),
        "checks_html": _exists(results / "checks.html"),
        "metrics_html": _exists(results / "metrics.html"),
        "digest": _exists(digest),
        "locator": _exists(results / "locator.txt"),
    }
    if not files["smoke"]:
        action, reason = "stop", "smoke_missing"
    elif not files["report_html"]:
        action, reason = "evaluate_incomplete", "report_html_missing"
    elif not files["digest"]:
        action, reason = "audit", "digest_missing"
    else:
        action, reason = "record", "digest_present"
    return {
        "stem": cleaned,
        "action": action,
        "reason": reason,
        "files": files,
    }


def _scrape_audit_locator(root: Path, stem: str) -> str | None:
    path = root / "audit" / f"{stem}.py"
    if not path.is_file():
        return None
    match = _PERSISTED.search(path.read_text(encoding="utf-8"))
    if match is None:
        return None
    text = match.group(1).strip()
    if not text or text.startswith("<"):
        return None
    return text


def loop_locator(root: Path, stem: str) -> dict[str, Any]:
    """Return the persisted-report locator without opening the Project."""
    cleaned = stem.strip()
    if not cleaned:
        raise ValueError("stem is required")
    path = _results_dir(root, cleaned) / "locator.txt"
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return {
                "stem": cleaned,
                "action": "proceed",
                "reason": "file",
                "locator": text,
            }
    scraped = _scrape_audit_locator(root, cleaned)
    if scraped is not None:
        return {
            "stem": cleaned,
            "action": "proceed",
            "reason": "audit",
            "locator": scraped,
        }
    return {
        "stem": cleaned,
        "action": "proceed",
        "reason": "missing",
        "locator": MISSING_LOCATOR,
    }


def render_loop(payload: dict[str, Any]) -> str:
    """Serialize a loop-gate payload."""
    return json.dumps(payload, indent=2) + "\n"
