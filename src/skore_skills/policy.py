"""Load and save ``.skore-workspace.json`` without touching hub credentials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

POLICY_FILENAME = ".skore-workspace.json"
HUB_CREDENTIALS = ".skore"

AUTOCOMMIT_VALUES = ("off", "ask", "on")
LOOP_STAGES = ("setup", "eda", "implement", "evaluate", "audit", "backlog")

POLICY_SET_KEYS = (
    "env_manager",
    "package",
    "tabular",
    "skore_mode",
    "git.autocommit",
    "loop.stage",
    "loop.stem",
)


def empty_policy() -> dict[str, Any]:
    """Return the default policy mapping."""
    return {
        "env_manager": None,
        "package": None,
        "tabular": None,
        "skore_mode": None,
        "git": {"autocommit": "ask"},
        "loop": {"stage": None, "stem": None},
    }


def policy_path(root: Path) -> Path:
    """Return the policy file path under ``root``."""
    return root / POLICY_FILENAME


def _merge_loaded(raw: Any) -> dict[str, Any]:
    data = empty_policy()
    if not isinstance(raw, dict):
        return data
    for key in ("env_manager", "package", "tabular", "skore_mode"):
        if key in raw:
            data[key] = raw[key]
    git = raw.get("git")
    if isinstance(git, dict) and "autocommit" in git:
        data["git"] = {"autocommit": git["autocommit"]}
    loop = raw.get("loop")
    if isinstance(loop, dict):
        merged = dict(data["loop"])
        if "stage" in loop:
            merged["stage"] = loop["stage"]
        if "stem" in loop:
            merged["stem"] = loop["stem"]
        data["loop"] = merged
    return data


def load_policy(root: Path) -> dict[str, Any]:
    """Read policy from disk, or defaults when the file is missing."""
    path = policy_path(root)
    if not path.is_file():
        return empty_policy()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _merge_loaded(raw)


def save_policy(root: Path, policy: dict[str, Any]) -> Path:
    """Write ``policy`` to ``.skore-workspace.json``.

    Parameters
    ----------
    root : pathlib.Path
        Project root.
    policy : dict
        Mapping to serialize.

    Returns
    -------
    pathlib.Path
        Path written.

    Raises
    ------
    ValueError
        If ``root`` is the hub credentials directory ``.skore``.
    """
    if root.name == HUB_CREDENTIALS:
        raise ValueError("refusing to write hub credentials path .skore")
    dest = policy_path(root)
    dest.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
    return dest


def set_policy_value(root: Path, key: str, value: str) -> dict[str, Any]:
    """Update one dotted policy key and persist.

    Raises
    ------
    ValueError
        Unknown key, invalid enum, or credentials collision.
    """
    if key not in POLICY_SET_KEYS:
        raise ValueError(f"unknown policy key: {key}")
    parsed: Any = None if value in {"", "null", "none"} else value
    if key == "git.autocommit":
        if parsed not in AUTOCOMMIT_VALUES:
            raise ValueError("git.autocommit must be off, ask, or on")
    if key == "loop.stage" and parsed is not None and parsed not in LOOP_STAGES:
        raise ValueError(f"loop.stage must be one of {', '.join(LOOP_STAGES)}")
    policy = load_policy(root)
    if key.startswith("git."):
        policy["git"][key.split(".", 1)[1]] = parsed
    elif key.startswith("loop."):
        policy["loop"][key.split(".", 1)[1]] = parsed
    else:
        policy[key] = parsed
    save_policy(root, policy)
    return policy


def infer_loop_stage(root: Path, policy: dict[str, Any], snapshot: dict[str, Any]) -> str:
    """Return policy stage or a filesystem-derived stage."""
    recorded = policy.get("loop", {}).get("stage")
    if recorded in LOOP_STAGES:
        return str(recorded)
    if not snapshot.get("has_src") and not snapshot.get("has_journal"):
        return "setup"
    if snapshot.get("eda") != "present":
        return "eda"
    stem = policy.get("loop", {}).get("stem") or snapshot.get("last_history_stem")
    if not stem:
        return "implement"
    if not (root / "tests" / "smoke" / f"test_{stem}.py").is_file():
        return "implement"
    if not (root / "audit" / f"{stem}.py").is_file():
        reports = root / "reports"
        if reports.is_dir() and any(reports.iterdir()):
            return "audit"
        return "evaluate"
    return "backlog"
