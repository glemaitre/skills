"""Run the per-stem smoke pytest and print a JSON gate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def smoke_test_path(root: Path, stem: str) -> Path:
    """Return ``tests/smoke/test_<stem>.py``."""
    return root / "tests" / "smoke" / f"test_{stem}.py"


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def run_smoke(root: Path, stem: str) -> tuple[dict[str, Any], int]:
    """Run pytest on the stem's smoke file. Stream pytest; return JSON + code."""
    cleaned = stem.strip()
    if not cleaned:
        raise ValueError("stem is required")
    path = smoke_test_path(root, cleaned)
    rel = _rel(root, path)
    if not path.is_file():
        return (
            {
                "stem": cleaned,
                "path": rel,
                "action": "stop",
                "reason": "smoke_missing",
                "exit_code": None,
            },
            1,
        )
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(path)],
        cwd=root,
        check=False,
    )
    if completed.returncode == 0:
        return (
            {
                "stem": cleaned,
                "path": rel,
                "action": "proceed",
                "reason": "green",
                "exit_code": 0,
            },
            0,
        )
    return (
        {
            "stem": cleaned,
            "path": rel,
            "action": "stop",
            "reason": "red",
            "exit_code": completed.returncode,
        },
        completed.returncode,
    )


def render_smoke(payload: dict[str, Any]) -> str:
    """Serialize a smoke-run payload."""
    return json.dumps(payload, indent=2) + "\n"
