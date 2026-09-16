"""Detect the project env manager and emit install / init commands."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from importlib.resources import files
from pathlib import Path
from typing import Any

from skore_skills.policy import load_policy
from skore_skills.style import RUFF_PYPROJECT_TABLE, ensure_ruff_in_pyproject
from skore_skills.workspace import MANAGER_ORDER, manager_evidence

HATCH_ADD_HINT = (
    "hatch has no universal add command; edit pyproject.toml "
    "[project] dependencies or [tool.hatch.envs.<env>.dependencies], "
    "then `hatch run`"
)
NO_MANAGER = "no env manager detected; record one before installing packages"
AMBIGUOUS = "multiple env managers are visible; do not pick automatically"
UNMANAGED = "environment is user-managed (env.managed is false); do not install"
PIXI_TOML_PRESENT = (
    "pixi.toml already exists; refuse to add [tool.pixi] to pyproject.toml"
)
INIT_EXISTS = "manager tables already present; pass --force to replace them"
INIT_MISMATCH = "detected manager {detected!r} does not match --manager {wanted!r}"
AGENT_PACKAGES = ("ruff", "ipython", "ipykernel")

_SKELETON = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "workspace"
version = "0.1.0"
description = "ML experimentation workspace."
requires-python = ">=3.11"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["src"]
"""

_PIXI_TABLE = """
[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]

[tool.pixi.feature.agent.dependencies]
ruff = "*"
ipython = "*"
ipykernel = "*"

[tool.pixi.environments]
default = { features = ["default"], solve-group = "default" }
agent = { features = ["default", "agent"], solve-group = "default" }
"""

_UV_GROUPS = """
[tool.uv]

[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_PIP_GROUPS = """
[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_POETRY_GROUPS = """
[tool.poetry]
package-mode = false

[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_HATCH_ENV = """
[tool.hatch.envs.default]

[tool.hatch.envs.agent]
dependencies = ["ruff", "ipython", "ipykernel"]
"""

_CONDA_DEFAULT = """\
name: workspace
channels:
  - conda-forge
dependencies:
  - python>=3.11
"""

_CONDA_AGENT = """\
name: workspace-agent
channels:
  - conda-forge
dependencies:
  - python>=3.11
  - ruff
  - ipython
  - ipykernel
"""


def load_stack_policy() -> dict[str, Any]:
    """Load packaged ``python-stack.json`` policy."""
    path = files("skore_skills").joinpath("data/python-stack.json")
    return json.loads(path.read_text(encoding="utf-8"))


_CONDA_PREFIX_MARKERS = (
    "miniconda",
    "miniconda3",
    "mambaforge",
    "micromamba",
    "anaconda",
    "anaconda3",
)


def _resolve_skore_binary() -> Path | None:
    """Return the real path of ``skore`` or ``skore-cli`` on PATH."""
    for name in ("skore", "skore-cli"):
        found = shutil.which(name)
        if found is None:
            continue
        path = Path(found)
        try:
            return path.resolve()
        except OSError:
            return path
    return None


def _manager_from_skore_path(path: Path) -> str | None:
    """Map a ``skore`` install path to a project manager, or None if weak."""
    parts = [part.lower() for part in path.parts]
    posix = path.as_posix().lower()
    if "pipx" in parts:
        return None
    if ".pixi" in parts or "/pixi/bin/" in posix:
        return "pixi"
    uv_tool = os.environ.get("UV_TOOL_DIR")
    if uv_tool:
        try:
            if path.resolve().is_relative_to(Path(uv_tool).resolve()):
                return "uv"
        except (OSError, ValueError):
            pass
    if "uv" in parts and "tools" in parts:
        return "uv"
    if "/uv/tools/" in posix:
        return "uv"
    parent = path.parent
    prefix = parent.parent if parent.name in {"bin", "Scripts"} else parent
    if (prefix / "conda-meta").is_dir():
        return "conda"
    if any(marker in parts for marker in _CONDA_PREFIX_MARKERS):
        return "conda"
    return None


def skore_cli_provenance() -> dict[str, str | None]:
    """Return how ``skore`` was installed, for ``recommended`` ranking only."""
    path = _resolve_skore_binary()
    if path is None:
        return {"manager": None, "path": None}
    return {"manager": _manager_from_skore_path(path), "path": str(path)}


def _recorded_manager(root: Path) -> str | None:
    recorded = load_policy(root).get("env_manager")
    if recorded in MANAGER_ORDER:
        return recorded
    return None


def _order_with_lead(lead: str | None) -> list[str]:
    order = list(MANAGER_ORDER)
    if lead in order:
        order.remove(lead)
        order.insert(0, lead)
    return order


def _recommended(
    root: Path,
    evidence: dict[str, list[str]],
    provenance_manager: str | None,
) -> list[str]:
    """Return manager names in ask order.

    Policy, then a unique manifest, then ``skore`` provenance, then
    ``MANAGER_ORDER``.
    """
    recorded = _recorded_manager(root)
    present = [name for name in MANAGER_ORDER if name in evidence]
    if recorded is not None:
        return _order_with_lead(recorded)
    if len(present) == 1:
        return present
    if present:
        return [name for name in MANAGER_ORDER if name in present]
    if provenance_manager in MANAGER_ORDER:
        return _order_with_lead(provenance_manager)
    return list(MANAGER_ORDER)


def _mismatch(root: Path, evidence: dict[str, list[str]]) -> bool:
    recorded = _recorded_manager(root)
    present = [name for name in MANAGER_ORDER if name in evidence]
    return recorded is not None and len(present) == 1 and present[0] != recorded


def detect(root: Path) -> dict[str, Any]:
    """Return detection JSON for ``root``.

    When two or more managers are visible, ``ambiguous`` is true and
    ``env_manager`` is null — the CLI must not pick a winner.
    ``recommended`` may still rank a recorded policy or ``skore``
    provenance; those do not change ``env_manager``.
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
    provenance = skore_cli_provenance()
    return {
        "env_manager": env_manager,
        "managers": managers,
        "evidence": evidence,
        "ambiguous": ambiguous,
        "mismatch": _mismatch(root, evidence),
        "recommended": _recommended(root, evidence, provenance["manager"]),
        "provenance": provenance,
        "managed": load_policy(root).get("env", {}).get("managed"),
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


def install_argv(
    manager: str,
    packages: list[str],
    *,
    feature: str | None = None,
) -> list[str] | None:
    """Return the manager-specific add command, or None for hatch."""
    extra: list[str] = []
    if feature:
        if manager == "pixi":
            extra = ["--feature", feature]
        elif manager in {"uv", "poetry"}:
            extra = ["--group", feature]
    commands: dict[str, list[str]] = {
        "pixi": ["pixi", "add", *extra, *packages],
        "uv": ["uv", "add", *extra, *packages],
        "poetry": ["poetry", "add", *extra, *packages],
        "conda": ["conda", "install", "-c", "conda-forge", *packages],
        "pip-venv": ["pip", "install", *packages],
    }
    if manager == "hatch":
        return None
    if manager not in commands:
        raise ValueError(f"unknown manager {manager!r}")
    return commands[manager]


def _unmanaged(root: Path) -> bool:
    return load_policy(root).get("env", {}).get("managed") is False


def add_packages(
    root: Path,
    packages: list[str],
    *,
    execute: bool = False,
    feature: str | None = None,
) -> tuple[str, int]:
    """Build (or run) install commands for ``packages``.

    Default is print-only. Never emits ``pip install`` for pixi.
    """
    if not packages:
        return "need at least one package\n", 2
    if _unmanaged(root):
        return UNMANAGED + "\n", 1
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
    argv = install_argv(str(manager), packages, feature=feature)
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


def _ensure_pyproject(root: Path) -> Path:
    path = root / "pyproject.toml"
    if not path.is_file():
        path.write_text(_SKELETON + "\n" + RUFF_PYPROJECT_TABLE, encoding="utf-8")
    else:
        ensure_ruff_in_pyproject(path)
    return path


def _append_if_missing(path: Path, marker: str, block: str, *, force: bool) -> bool:
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if marker in text and not force:
        return False
    if marker in text and force:
        # Keep existing file; caller treats False as already-present.
        return False
    path.write_text(text.rstrip() + "\n" + block.strip() + "\n", encoding="utf-8")
    return True


def init_environment(
    root: Path,
    manager: str,
    *,
    force: bool = False,
) -> tuple[str, int]:
    """Write manager + agent tables. Does not create ``src/`` or install."""
    if manager not in MANAGER_ORDER:
        return f"unknown manager {manager!r}\n", 2
    if _unmanaged(root):
        return UNMANAGED + "\n", 1
    payload = detect(root)
    detected = payload["env_manager"]
    if detected not in {None, "none", manager}:
        return INIT_MISMATCH.format(detected=detected, wanted=manager) + "\n", 1
    if manager == "pixi" and (root / "pixi.toml").is_file():
        return PIXI_TOML_PRESENT + "\n", 1

    written: list[str] = []
    if manager == "conda":
        default = root / "environment.yml"
        agent = root / "environment-agent.yml"
        if default.is_file() and not force:
            return INIT_EXISTS + "\n", 1
        default.write_text(_CONDA_DEFAULT, encoding="utf-8")
        agent.write_text(_CONDA_AGENT, encoding="utf-8")
        written.extend(["environment.yml", "environment-agent.yml"])
        follow = "conda env create -f environment-agent.yml"
        return "wrote " + ", ".join(written) + f"\nnext: {follow}\n", 0

    path = _ensure_pyproject(root)
    if manager == "pixi":
        added = _append_if_missing(path, "[tool.pixi", _PIXI_TABLE, force=force)
        follow = "pixi install -e agent"
    elif manager == "uv":
        added = _append_if_missing(path, "[tool.uv]", _UV_GROUPS, force=force)
        follow = "uv sync --group agent"
    elif manager == "poetry":
        added = _append_if_missing(path, "[tool.poetry]", _POETRY_GROUPS, force=force)
        follow = "poetry install --with agent"
    elif manager == "hatch":
        added = _append_if_missing(
            path, "[tool.hatch.envs.agent]", _HATCH_ENV, force=force
        )
        follow = "hatch env create agent"
    else:
        added = _append_if_missing(
            path, "[dependency-groups]", _PIP_GROUPS, force=force
        )
        req = root / "requirements.txt"
        if not req.is_file() or force:
            req.write_text("ruff\nipython\nipykernel\n", encoding="utf-8")
            added = True
        follow = "python -m venv .venv && .venv/bin/pip install -r requirements.txt"
    if not added:
        return INIT_EXISTS + "\n", 1
    return f"updated {path.name}\nnext: {follow}\n", 0
