"""Tests for ``skore_skills cells run``."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from skore_skills.cli import cli

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_notebook.py"


def _digest(text: str) -> str:
    """Drop the source path line so CLI vs shim paths can differ."""
    lines = text.splitlines(keepends=True)
    if lines and lines[0].startswith("# Cells:"):
        lines[0] = "# Cells: `<src>`\n"
    return "".join(lines)


def test_cells_run_digest_and_dest(tmp_path: Path) -> None:
    """CLI digest includes markdown, stdout, last-expr, and errors; dest matches."""
    dest = tmp_path / "out.md"
    result = CliRunner().invoke(cli, ["cells", "run", str(FIXTURE), str(dest)])
    assert result.exit_code == 0, result.output
    assert "Title" in result.output
    assert "hello" in result.output
    assert "2 + 2" in result.output
    assert "ValueError" in result.output
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == result.output


def test_cells_run_missing_file() -> None:
    """Missing source exits non-zero."""
    result = CliRunner().invoke(cli, ["cells", "run", "no-such-notebook.py"])
    assert result.exit_code != 0


def test_shim_matches_cli() -> None:
    """Skill shim stdout matches ``python -m skore_skills cells run``."""
    shim = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "audit-ml-pipeline"
        / "scripts"
        / "run_cells.py"
    )
    cli_proc = subprocess.run(
        [sys.executable, "-m", "skore_skills", "cells", "run", str(FIXTURE)],
        check=False,
        capture_output=True,
        text=True,
    )
    shim_proc = subprocess.run(
        [sys.executable, str(shim), str(FIXTURE)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert cli_proc.returncode == 0, cli_proc.stderr
    assert shim_proc.returncode == 0, shim_proc.stderr
    assert _digest(cli_proc.stdout) == _digest(shim_proc.stdout)
