"""Tests for ``skore_skills git ignore-merge`` and ``git end-turn``."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.git import merge_gitignore
from skore_skills.policy import set_policy_value

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(root: Path) -> None:
    _git(root, "init")


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_end_turn_no_repo_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing ``.git`` skips without nagging."""
    monkeypatch.chdir(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "eda"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "no_repo"
    assert payload["skill"] == "persist-ml-git"


def test_end_turn_unanswered_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unanswered autocommit never asks persist."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "unanswered"


def test_end_turn_off_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``off`` skips even when the tree is dirty."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "off")
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "off"


def test_end_turn_on_invokes_persist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``on`` plus a dirty tree names ``persist-ml-git`` and does not commit."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "persist"
    assert payload["skill"] == "persist-ml-git"
    assert "src/pkg/data.py" in payload["staged"]
    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert head.returncode != 0


def test_end_turn_ambiguous_invokes_resolve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown hidden files still invoke persist to ask the user."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "eda"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "resolve-dotfiles"
    assert ".python-version" in payload["ambiguous_dotfiles"]


def test_end_turn_clean_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A clean tree with autocommit on is a skip."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", "--", ".gitignore")
    _git(tmp_path, "commit", "-m", "ignore")
    set_policy_value(tmp_path, "git.autocommit", "on")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] in {"clean", "nothing_to_commit"}


def test_ignore_merge_additive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Existing ignore lines are kept; packaged patterns are appended."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".gitignore", "custom-keep/\n")
    result = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "custom-keep/" in text
    assert "scratch/" in text
    assert ".*" in text
    payload = json.loads(result.output)
    assert payload["action"] == "ready"


def test_merge_gitignore_is_idempotent(tmp_path: Path) -> None:
    """A second merge adds no duplicate patterns."""
    first = merge_gitignore(tmp_path)
    second = merge_gitignore(tmp_path)
    assert first
    assert second == []


def test_ignore_merge_ambiguous_dotfile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``ignore-merge`` reports unknown hidden paths and exits 2."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert result.exit_code == 2, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "resolve-dotfiles"
    assert ".python-version" in payload["ambiguous_dotfiles"]


def test_ignore_merge_keep_clears_ambiguity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``ignore-merge --keep`` drops a path from the ambiguous list."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(
        cli, ["git", "ignore-merge", "--keep", ".python-version"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "ready"
    assert payload["ambiguous_dotfiles"] == []


def test_ignore_merge_rejects_keep_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Secrets cannot be force-tracked."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli, ["git", "ignore-merge", "--keep", ".env"]
    )
    assert result.exit_code != 0
    assert "blocked" in result.output.lower() or "keep" in result.output.lower()
