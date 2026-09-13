"""Tests for ``skore_skills env detect`` / ``env add``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.env import install_argv, load_stack_policy

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "envs"


@pytest.mark.parametrize(
    ("name", "manager"),
    [
        ("pixi", "pixi"),
        ("uv", "uv"),
        ("poetry", "poetry"),
        ("hatch", "hatch"),
        ("conda", "conda"),
        ("pip-venv", "pip-venv"),
        ("none", "none"),
    ],
)
def test_env_detect_each_manager(
    name: str, manager: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each fixture maps to the documented manager (or none)."""
    monkeypatch.chdir(FIXTURES / name)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == manager
    assert payload["ambiguous"] is False


def test_env_detect_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    """pixi.toml + conda env is ambiguous: JSON flag and non-zero exit."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ambiguous"] is True
    assert payload["env_manager"] is None
    assert payload["managers"] == ["pixi", "conda"]


def test_env_add_pixi_never_pip(monkeypatch: pytest.MonkeyPatch) -> None:
    """``env add`` on a pixi fixture prints ``pixi add``, never ``pip install``."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pixi add skrub"
    assert "pip install" not in result.output


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("uv", "uv add pandas"),
        ("poetry", "poetry add pandas"),
        ("conda", "conda install -c conda-forge pandas"),
        ("pip-venv", "pip install pandas"),
    ],
)
def test_env_add_command_per_manager(
    fixture: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Print-only add matches the env-manager command table."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_add_hatch_prints_edit_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hatch has no add command; print an edit hint and never pip."""
    monkeypatch.chdir(FIXTURES / "hatch")
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert "edit pyproject.toml" in result.output
    assert "pip install" not in result.output
    executed = CliRunner().invoke(cli, ["env", "add", "--execute", "pandas"])
    assert executed.exit_code != 0
    assert "pip install" not in executed.output


def test_env_add_forbidden_substitute(monkeypatch: pytest.MonkeyPatch) -> None:
    """Known substitutes are refused using python-stack.json."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "xgboost"])
    assert result.exit_code != 0
    assert "HistGradientBoosting" in result.output
    policy = load_stack_policy()
    assert "xgboost" in policy["forbidden_substitutes"]
    assert "scikit-learn" in policy["mandatory"]


def test_env_add_ambiguous_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not install into an ambiguous workspace."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "multiple env managers" in result.output


def test_env_add_none_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nothing detected: do not invent pip."""
    monkeypatch.chdir(FIXTURES / "none")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "no env manager" in result.output
    assert "pip install" not in result.output


def test_env_add_requires_package() -> None:
    """``env add`` without packages is usage error."""
    result = CliRunner().invoke(cli, ["env", "add"])
    assert result.exit_code != 0


def test_env_add_execute_runs_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``--execute`` runs the printed command."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--execute", "skrub"])
    assert result.exit_code == 0, result.output
    assert seen == [["pixi", "add", "skrub"]]
    assert result.output.strip() == "pixi add skrub"


def test_install_argv_unknown_manager() -> None:
    """Unknown manager names are a programming error."""
    with pytest.raises(ValueError, match="unknown manager"):
        install_argv("pants", ["x"])


def test_add_packages_empty_list(tmp_path: Path) -> None:
    """Library callers still get a usage error for an empty package list."""
    from skore_skills.env import add_packages

    text, code = add_packages(tmp_path, [])
    assert code == 2
    assert "at least one package" in text
