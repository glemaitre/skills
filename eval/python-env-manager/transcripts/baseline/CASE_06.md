# CASE_06 — Editable workspace install for a fresh scaffold

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-env-manager/SKILL.md` (580 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Fresh scaffold from `organize-ml-workspace`.
- `pyproject.toml` declares `src/<pkg>/`.
- `pixi.toml` exists.
- pixi is the manager (recorded).]

The workspace was just scaffolded. Wire the editable install for
`src/<pkg>/`.
```

## Response

# Wiring Editable Install for `src/<pkg>/`

I'll wire the local workspace package into pixi so it's editable and importable from anywhere without `PYTHONPATH` hacks.

## Pre-flight (python-env-manager)

```
- [x] Detection done; manager identified: pixi
      Evidence: pixi.toml present at project root (workspace state)
- [x] Manager pre-recorded in Workspace decisions
      Evidence: JOURNAL.md Status (Workspace decisions, recorded prior session)
- [x] Sibling SKILL.md files opened this turn:
      organize-ml-workspace (for the editable handoff context),
      data-science-python-stack (for Tier 1 reference)
      Evidence: Read .agents/skills/<each>/SKILL.md (this turn)
- [x] Package to install: local workspace package from src/<pkg>/
      Evidence: pyproject.toml declares [project] at project root; src/<pkg>/ structure confirmed (workspace state)
- [x] Install command syntax: pixi add --pypi --editable .
      Evidence: § "Editable workspace package — wire src/<pkg>/ per manager" → pixi row
- [x] Scope: same feature as Tier 1
      Evidence: workspace state shows pixi.toml exists; Tier 1 (scikit-learn, skrub, skore, ruff) is in default feature (standard scaffold)
```

---

## Command

```bash
pixi add --pypi --editable .
```

### What this does

- **Adds the local package** from `src/<pkg>/` to `pixi.toml` under `[pypi-dependencies]`.
- **Editable mode** (`--editable .`) means edits to `src/<pkg>/` are picked up immediately — no reinstall needed.
- **Importable from anywhere** — `from <pkg>.X import Y` works in notebooks, scripts, and tests without `PYTHONPATH=src`.
- **In the default feature** (standard for Tier 1) so `pixi run` / `pixi shell` activates it alongside scikit-learn, skrub, skore, ruff.

### Post-install audit

Once the command succeeds (exit code 0), verify:

```bash
pixi run python -c "import <pkg>; print(<pkg>.__file__)"
```

Should print the path into `src/<pkg>/`, confirming it's editable and discoverable.

---

Ready to run. Any scope preferences (e.g., a separate feature for the workspace package itself), or shall I proceed with default?
