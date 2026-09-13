"""Detect the project env manager and emit install commands."""

from __future__ import annotations

import json
import subprocess
from importlib.resources import files
from pathlib import Path
from typing import Any

from skore_skills.workspace import MANAGER_ORDER, manager_evidence

HATCH_ADD_HINT = (
    "hatch has no universal add command; edit pyproject.toml "
    "[project] dependencies or [tool.hatch.envs.<env>.dependencies], "
    "then `hatch run`"
)
NO_MANAGER = "no env manager detected; record one before installing packages"
AMBIGUOUS = "multiple env managers are visible; do not pick automatically"


def load_stack_policy() -> dict[str, Any]:
    """Load packaged ``python-stack.json`` policy."""
    path = files("skore_skills").joinpath("data/python-stack.json")
    return json.loads(path.read_text(encoding="utf-8"))


def detect(root: Path) -> dict[str, Any]:
    """Return detection JSON for ``root``.

    When two or more managers are visible, ``ambiguous`` is true and
    ``env_manager`` is null — the CLI must not pick a winner.
    """
    evidence = manager_evidence(root)
    managers = [name for name in MANAGER_ORDER if name in evidence]
    ambiguous = len(managers) > 1
    if not managers:
        env_manager: str | None = "none"
    elif ambiguous:
        env_manager = None
    else:
        env_manager = managers[0]
    return {
        "env_manager": env_manager,
        "managers": managers,
        "evidence": evidence,
        "ambiguous": ambiguous,
    }


def forbidden_reason(package: str) -> str | None:
    """Return a refusal message if ``package`` is a known substitute."""
    policy = load_stack_policy()
    substitutes = policy["forbidden_substitutes"]
    key = package.strip().lower().split("[", 1)[0]
    message = substitutes.get(key)
    if isinstance(message, str):
        return message
    return None


def install_argv(manager: str, packages: list[str]) -> list[str] | None:
    """Return the manager-specific add command, or None for hatch."""
    commands: dict[str, list[str]] = {
        "pixi": ["pixi", "add", *packages],
        "uv": ["uv", "add", *packages],
        "poetry": ["poetry", "add", *packages],
        "conda": ["conda", "install", "-c", "conda-forge", *packages],
        "pip-venv": ["pip", "install", *packages],
    }
    if manager == "hatch":
        return None
    if manager not in commands:
        raise ValueError(f"unknown manager {manager!r}")
    return commands[manager]


def add_packages(
    root: Path,
    packages: list[str],
    *,
    execute: bool = False,
) -> tuple[str, int]:
    """Build (or run) install commands for ``packages``.

    Default is print-only. Never emits ``pip install`` for pixi.
    """
    if not packages:
        return "need at least one package\n", 2
    for name in packages:
        reason = forbidden_reason(name)
        if reason is not None:
            return reason + "\n", 1
    payload = detect(root)
    if payload["ambiguous"]:
        return AMBIGUOUS + "\n", 1
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return NO_MANAGER + "\n", 1
    argv = install_argv(str(manager), packages)
    if argv is None:
        text = HATCH_ADD_HINT + "\n"
        if execute:
            return text + "refusing --execute for hatch (no add command)\n", 1
        return text, 0
    rendered = " ".join(argv) + "\n"
    if not execute:
        return rendered, 0
    completed = subprocess.run(argv, check=False)
    return rendered, completed.returncode
