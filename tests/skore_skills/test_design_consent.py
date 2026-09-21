"""Tests for ``skore-skills design consent``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.design_consent import design_consent


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _note(root: Path, stem: str, state: str) -> None:
    _write(
        root / "journal" / f"{stem}.md",
        "## Status\n\n"
        f"- **State:** {state}\n"
        "- **Approved by user on:** n/a\n",
    )


def test_planned_asks_for_approval(tmp_path: Path) -> None:
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "ask",
        "reason": "first_approval",
        "choices": ["approve", "modify", "stop"],
    }


def test_approved_is_proceed(tmp_path: Path) -> None:
    stem = "01_baseline"
    _note(tmp_path, stem, "approved")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "proceed",
        "reason": "approved",
    }
    assert "choices" not in payload


@pytest.mark.parametrize("state", ["running", "done"])
def test_running_and_done_are_proceed(tmp_path: Path, state: str) -> None:
    stem = "02_next"
    _note(tmp_path, stem, state)

    payload = design_consent(tmp_path, stem)

    assert payload["action"] == "proceed"
    assert payload["reason"] == state


def test_missing_design_is_stop(tmp_path: Path) -> None:
    payload = design_consent(tmp_path, "09_missing")

    assert payload == {
        "stem": "09_missing",
        "action": "stop",
        "reason": "missing_design",
    }


def test_abandoned_is_stop(tmp_path: Path) -> None:
    stem = "03_old"
    _note(tmp_path, stem, "abandoned — paper's required dep was non-trivial")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "stop",
        "reason": "abandoned",
    }


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        design_consent(Path("."), "  ")


def test_cli_prints_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["design", "consent", "--stem", stem])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "ask"


def test_cli_requires_stem() -> None:
    result = CliRunner().invoke(cli, ["design", "consent"])

    assert result.exit_code == 2
    assert "Missing option" in result.output
