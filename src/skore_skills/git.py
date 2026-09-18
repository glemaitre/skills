"""Gitignore merge and a read-only end-turn hook.

Never runs ``git init``, ``git add``, or ``git commit``. Those stay
on the real git CLI, driven by ``setup-git`` and ``persist-ml-git``.
"""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from skore_skills.policy import load_policy
from skore_skills.scaffold import template_root

END_TURN_STAGES = ("setup", "data_analysis", "implement", "evaluate", "backlog")
PERSIST_SKILL = "persist-ml-git"

KEEP_EXCEPTIONS = frozenset({".gitignore", ".gitattributes"})
MUST_IGNORE_DOTFILES = frozenset(
    {
        ".env",
        ".skore",
        ".pixi",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".DS_Store",
        ".idea",
        ".vscode",
        ".claude",
        ".coverage",
        ".git",
    }
)
BLOCKED_NAMES = frozenset({".env", ".skore"})
GIT_MISSING = "git is not installed on PATH"


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def _run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            env=_git_env(),
        )
    except FileNotFoundError as exc:
        raise ValueError(GIT_MISSING) from exc


def _has_repo(root: Path) -> bool:
    return (root / ".git").exists()


def _is_blocked(rel: str) -> bool:
    path = Path(rel)
    return any(part in BLOCKED_NAMES or part.startswith(".env") for part in path.parts)


def _resolve_keep(root: Path, keep: Sequence[str]) -> list[str]:
    resolved: list[str] = []
    root_resolved = root.resolve()
    for raw in keep:
        path = Path(raw)
        if path.is_absolute():
            try:
                rel = path.resolve().relative_to(root_resolved)
            except ValueError as exc:
                raise ValueError(f"keep path outside workspace: {raw}") from exc
        else:
            rel = path
        if ".." in rel.parts:
            raise ValueError(f"keep path outside workspace: {raw}")
        posix = rel.as_posix()
        if _is_blocked(posix):
            raise ValueError(f"refusing to keep blocked path: {posix}")
        resolved.append(posix)
    return resolved


def _keep_patterns(root: Path, posix: str) -> list[str]:
    target = root / posix
    if target.is_dir() or posix.endswith("/"):
        name = posix.rstrip("/")
        return [f"!{name}/", f"!{name}/**"]
    return [f"!{posix}"]


def _append_keep_exceptions(root: Path, keep: Sequence[str]) -> list[str]:
    dest = root / ".gitignore"
    existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
    existing_lines = {line.rstrip("\n") for line in existing.splitlines()}
    added: list[str] = []
    extra: list[str] = []
    for posix in keep:
        for pattern in _keep_patterns(root, posix):
            if pattern not in existing_lines:
                extra.append(pattern)
                existing_lines.add(pattern)
                added.append(pattern)
    if extra:
        body = existing.rstrip("\n")
        dest.write_text(body + "\n" + "\n".join(extra) + "\n", encoding="utf-8")
    return added


def merge_gitignore(root: Path) -> list[str]:
    """Union packaged ignore rules into ``root/.gitignore``.

    Never deletes user lines. Returns newly added pattern lines.
    """
    template = (template_root() / ".gitignore").read_text(encoding="utf-8")
    dest = root / ".gitignore"
    if not dest.is_file():
        dest.write_text(template, encoding="utf-8")
        return [
            line.strip()
            for line in template.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    existing = dest.read_text(encoding="utf-8")
    present = {
        line.strip()
        for line in existing.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    added: list[str] = []
    out_lines = existing.splitlines()
    for line in template.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped not in present:
            out_lines.append(line)
            present.add(stripped)
            added.append(stripped)
    dest.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return added


def list_ambiguous_dotfiles(root: Path, keep: Sequence[str] = ()) -> list[str]:
    """Return top-level ``.*`` paths that need a user decision."""
    kept = set(keep)
    names: list[str] = []
    if not root.is_dir():
        return names
    for path in sorted(root.iterdir(), key=lambda item: item.name):
        name = path.name
        if not name.startswith(".") or name in {".", ".."}:
            continue
        if name in KEEP_EXCEPTIONS or name in MUST_IGNORE_DOTFILES:
            continue
        if name in kept or f"{name}/" in kept:
            continue
        names.append(name + ("/" if path.is_dir() else ""))
    return names


def _porcelain_paths(root: Path) -> list[str]:
    proc = _run_git(root, "status", "--porcelain", "-uall")
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or "git status failed")
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        rest = line[3:]
        if " -> " in rest:
            rest = rest.split(" -> ", 1)[1]
        if rest.startswith('"') and rest.endswith('"'):
            rest = rest[1:-1]
        paths.append(rest.replace("\\", "/"))
    return paths


def _commit_candidates(root: Path) -> tuple[list[str], list[str]]:
    paths = _porcelain_paths(root)
    blocked = sorted({path for path in paths if _is_blocked(path)})
    staged = [path for path in paths if path not in blocked]
    return staged, blocked


def _payload(**fields: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "loop_stage": None,
        "autocommit": None,
        "repo": False,
        "skill": PERSIST_SKILL,
        "action": "skip",
        "reason": None,
        "status": [],
        "staged": [],
        "ambiguous_dotfiles": [],
        "blocked": [],
        "ignore_added": [],
    }
    base.update(fields)
    return base


def run_ignore_merge(
    root: Path, *, keep: Sequence[str] = ()
) -> tuple[dict[str, Any], int]:
    """Merge packaged ignore rules; do not run git."""
    keep_paths = _resolve_keep(root, keep)
    ignore_added = merge_gitignore(root)
    ignore_added.extend(_append_keep_exceptions(root, keep_paths))
    ambiguous = list_ambiguous_dotfiles(root, keep_paths)
    payload = _payload(
        action="resolve-dotfiles" if ambiguous else "ready",
        reason="ambiguous_dotfiles" if ambiguous else "ready",
        repo=_has_repo(root),
        autocommit=load_policy(root).get("git", {}).get("autocommit"),
        ambiguous_dotfiles=ambiguous,
        ignore_added=ignore_added,
    )
    return payload, (2 if ambiguous else 0)


def run_end_turn(root: Path, stage: str) -> tuple[dict[str, Any], int]:
    """Print whether to load ``persist-ml-git``. Never commits."""
    if stage not in END_TURN_STAGES:
        raise ValueError(f"stage must be one of {', '.join(END_TURN_STAGES)}")
    policy = load_policy(root)
    autocommit = policy.get("git", {}).get("autocommit")
    if not _has_repo(root):
        return (
            _payload(
                loop_stage=stage,
                autocommit=autocommit,
                repo=False,
                action="skip",
                reason="no_repo",
            ),
            0,
        )

    status = _porcelain_paths(root)
    ambiguous = list_ambiguous_dotfiles(root)
    staged, blocked = _commit_candidates(root)
    common = {
        "loop_stage": stage,
        "autocommit": autocommit,
        "repo": True,
        "status": status,
        "staged": staged,
        "blocked": blocked,
        "ambiguous_dotfiles": ambiguous,
    }
    if autocommit is None:
        return (_payload(**common, action="skip", reason="unanswered"), 0)
    if autocommit == "off":
        return (_payload(**common, action="skip", reason="off"), 0)
    if ambiguous:
        return (
            _payload(**common, action="invoke", reason="resolve-dotfiles"),
            0,
        )
    if not staged:
        reason = "clean" if not blocked else "nothing_to_commit"
        return (_payload(**common, action="skip", reason=reason), 0)
    return (_payload(**common, action="invoke", reason="persist"), 0)


def render_git_json(payload: dict[str, Any]) -> str:
    """Serialize a git command payload."""
    return json.dumps(payload, indent=2) + "\n"
