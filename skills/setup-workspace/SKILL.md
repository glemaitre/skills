---
name: setup-workspace
description: >
  Detect an existing ML workspace or scaffold a fresh one. Reusable
  code lives in `src/<pkg>/`; experiments are `# %%` scripts;
  design notes and index live in `journal/`. Existing conventions
  always win.

  TRIGGER for a new ML project layout or first scaffold.

  SKIP pipeline, evaluation, EDA, and library choice.

  HOW TO USE: detect first. For a fresh or manager-only layout,
  ask G-PKG-NAME, then `python -m skore_skills scaffold --package
  <pkg>`. For an existing layout, glue without renaming.
---

# Set Up Workspace

Decide where artifacts live. Do not design an experiment here.

## Detection

- `src/` or `experiments/` present → **existing**. Reuse names and
  folders. Do not scaffold again.
- Manager manifest without `src/<pkg>/` → **manager-only**. Still
  scaffold; keep existing `pyproject.toml`. No `--force`.
- Otherwise → **fresh**. Ask G-PKG-NAME, then scaffold.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] Layout: fresh | manager-only | existing
- [ ] G-PKG-NAME: ask if fresh/manager-only (unless src/<pkg>/ already matches)
- [ ] scaffold --package <pkg> | glue (existing; no --force)
- [ ] dispatched → return | standalone → git end-turn --stage setup
```

## Sequence

1. If fresh or manager-only, ask **G-PKG-NAME** (the `src/<pkg>/`
   import name; folder name as default). “You pick” does not
   resolve it. A matching `[project] name` + `src/<pkg>/` already
   resolves it.
2. Fresh / manager-only:

   ```bash
   python -m skore_skills scaffold --package <pkg>
   ```

3. Existing: add only glue the user asked for. No rename, no
   overwrite, no `--force`.
4. If the user wants a **new experiment**, load
   `iterate-ml-experiment` or `triage-ml-task` when installed. Do
   not write `experiments/NN_*.py` here.
5. If `setup-ml-project` dispatched this turn and is in this
   session, return to it; else stop. Standalone:
   `python -m skore_skills git end-turn --stage setup`. If JSON
   `action` is `invoke`, load `persist-ml-git` when installed.
   Then load `triage-ml-task` when installed.

## Stop conditions

- Do not ask env manager, tabular library, or skore mode.
- Do not run `pixi init` / `uv init`.
- Do not install packages or editable-install.
- Scaffold may leave an empty experiment shell. Do not write a
  runnable `build_learner` / `skore.evaluate` / `project.put` body.
- Do not evaluate or `project.put` from `scratch/`.
- Never `git commit` here.

## Layout (`scaffold` writes this)

```text
src/<pkg>/
experiments/
journal/JOURNAL.md
audit/
tests/smoke/
scratch/
reports/
data/
```
