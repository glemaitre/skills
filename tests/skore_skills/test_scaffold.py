"""Tests for ``skore_skills scaffold``."""

from __future__ import annotations

import ast
import compileall
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.scaffold import template_root

SKILL_TEMPLATES = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "organize-ml-workspace"
    / "templates"
)


def test_packaged_templates_match_skill_tree() -> None:
    """Package data stays in sync with organize-ml-workspace templates."""
    packaged = template_root()
    skill_files = sorted(
        path.name for path in SKILL_TEMPLATES.iterdir() if path.is_file()
    )
    pkg_files = sorted(path.name for path in packaged.iterdir() if path.is_file())
    assert pkg_files == skill_files
    for name in skill_files:
        assert (packaged / name).read_bytes() == (SKILL_TEMPLATES / name).read_bytes()


def test_scaffold_tree_and_no_placeholders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scaffold substitutes ``<pkg>`` and matches the skill file set."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert result.exit_code == 0, result.output
    src = tmp_path / "src" / "demo_pkg"
    assert (src / "__init__.py").is_file()
    assert (src / "data.py").is_file()
    assert (src / "features.py").is_file()
    assert (src / "pipeline.py").is_file()
    assert (src / "evaluate.py").is_file()
    assert (tmp_path / "experiments" / "01_baseline.py").is_file()
    assert (tmp_path / "pyproject.toml").is_file()
    assert (tmp_path / ".gitignore").is_file()
    assert (tmp_path / "journal" / "JOURNAL.md").is_file()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "demo-pkg"' in pyproject
    experiment = (tmp_path / "experiments" / "01_baseline.py").read_text(
        encoding="utf-8"
    )
    assert "from demo_pkg import PROJECT_ROOT" in experiment
    assert "<pkg>" not in experiment
    tree = ast.parse(experiment)
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"evaluate", "put"}
        for node in ast.walk(tree)
    )
    for path in tmp_path.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".toml", ".md"}:
            text = path.read_text(encoding="utf-8")
            assert "<pkg>" not in text
            assert "<SKORE_PROJECT_INIT>" not in text
    assert compileall.compile_dir(str(src), quiet=1)


def test_scaffold_refuses_without_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A second run on a complete layout exits non-zero unless ``--force``."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    first = runner.invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert first.exit_code == 0, first.output
    second = runner.invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert second.exit_code != 0
    assert "refusing" in second.output
    forced = runner.invoke(cli, ["scaffold", "--package", "demo_pkg", "--force"])
    assert forced.exit_code == 0, forced.output


def test_scaffold_requires_package() -> None:
    """``--package`` is mandatory."""
    result = CliRunner().invoke(cli, ["scaffold"])
    assert result.exit_code != 0


def test_scaffold_rejects_invalid_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hyphenated names are not importable package directories."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["scaffold", "--package", "demo-pkg"])
    assert result.exit_code != 0
    assert "identifier" in result.output
