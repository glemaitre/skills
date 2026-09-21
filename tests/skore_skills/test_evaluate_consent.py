"""Tests for ``skore-skills evaluate consent``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.evaluate_consent import evaluate_consent


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _smoke(root: Path, stem: str) -> None:
    _write(root / "tests" / "smoke" / f"test_{stem}.py", "def test_ok():\n    pass\n")


def test_first_eval_asks_when_report_is_placeholder(tmp_path: Path) -> None:
    stem = "05_new_model"
    _smoke(tmp_path, stem)
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## History\n\n"
        "| Stem | Intent (one line) | Status | Headline result | Report | Design note |\n"
        "|---|---|---|---|---|---|\n"
        f"| `{stem}` | try a new model | planned | n/a | n/a | "
        f"[design](./{stem}.md) |\n",
    )
    _write(
        tmp_path / "journal" / f"{stem}.md",
        "## Status\n\n"
        "- **Persisted report:** n/a — not persisted\n",
    )

    payload = evaluate_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "ask",
        "reason": "first_eval",
        "choices": ["evaluate", "modify", "stop"],
    }


def test_history_locator_is_proceed(tmp_path: Path) -> None:
    stem = "05_new_model"
    _smoke(tmp_path, stem)
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## History\n\n"
        "| Stem | Intent (one line) | Status | Headline result | Report | Design note |\n"
        "|---|---|---|---|---|---|\n"
        f"| `{stem}` | try a new model | done | 0.81 | "
        "[Open report](https://hub.example/report/42) | "
        f"[design](./{stem}.md) |\n",
    )

    payload = evaluate_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "proceed",
        "reason": "persisted_report",
    }
    assert "choices" not in payload


def test_design_note_locator_is_proceed(tmp_path: Path) -> None:
    stem = "01_baseline"
    _smoke(tmp_path, stem)
    _write(
        tmp_path / "journal" / f"{stem}.md",
        "## Status\n\n"
        "- **Persisted report:** local workspace: [reports/](../reports/) "
        "· id: local-report-id\n",
    )

    payload = evaluate_consent(tmp_path, stem)

    assert payload["action"] == "proceed"
    assert payload["reason"] == "persisted_report"


def test_missing_smoke_is_stop_even_with_locator(tmp_path: Path) -> None:
    stem = "05_new_model"
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## History\n\n"
        "| Stem | Intent (one line) | Status | Headline result | Report | Design note |\n"
        "|---|---|---|---|---|---|\n"
        f"| `{stem}` | try a new model | done | 0.81 | "
        "[Open report](https://hub.example/report/42) | note |\n",
    )

    payload = evaluate_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "stop",
        "reason": "smoke_missing",
    }


def test_missing_stem_with_smoke_is_ask(tmp_path: Path) -> None:
    stem = "09_unlisted"
    _smoke(tmp_path, stem)

    payload = evaluate_consent(tmp_path, stem)

    assert payload["action"] == "ask"
    assert payload["reason"] == "first_eval"


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        evaluate_consent(Path("."), "  ")


def test_cli_prints_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stem = "05_new_model"
    _smoke(tmp_path, stem)
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["evaluate", "consent", "--stem", stem])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "ask"


def test_cli_requires_stem() -> None:
    result = CliRunner().invoke(cli, ["evaluate", "consent"])

    assert result.exit_code == 2
    assert "Missing option" in result.output
