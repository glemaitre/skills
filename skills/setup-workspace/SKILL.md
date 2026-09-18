---
name: setup-workspace
description: >
  Detect an existing ML workspace or scaffold a fresh one via
  `python -m skore_skills scaffold --package <pkg>`. Cookiecutter
  only: directories, README.md files, and src/<pkg>/ stubs. After
  a first scaffold, ask once for executed notebooks and/or a
  documentation site.

  TRIGGER for a new ML project layout or first scaffold.

  SKIP pipeline, evaluation, exploratory data analysis, and library
  choice.

  HOW TO USE: detect first. For a fresh or manager-only layout,
  resolve G-PKG-NAME only via `AskUserQuestion`, then scaffold,
  then the notebooks/site gate. For an existing layout, stop
  without scaffolding or inventing files.
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
- [ ] scaffold --package <pkg> | existing: no scaffold, no invent
- [ ] fresh/manager-only: notebooks + site gate; persist; install
- [ ] dispatched → return | standalone → git end-turn --stage setup
```

## Sequence

1. If fresh or manager-only, resolve **G-PKG-NAME** only via the
   `AskUserQuestion` tool (the `src/<pkg>/` import name; folder
   name as the default option). “You pick” / “go fast” does not
   resolve it. Do not confirm in prose instead of the tool. A
   matching `[project] name` + `src/<pkg>/` already resolves it —
   do not re-ask.
2. Fresh / manager-only:

   ```bash
   python -m skore_skills scaffold --package <pkg>
   ```

   The CLI writes the tree and each folder `README.md`. Do not
   recreate those files from memory.
3. Existing: do not scaffold again. Do not invent files. No
   rename, no overwrite, no `--force`. Do not ask the
   notebooks/site gate.
4. After scaffold on fresh or manager-only, if
   `policy.notebooks` and `policy.site` are both `null`
   (never asked): **AskUserQuestion** with `allow_multiple`, both
   boxes **unchecked** by default:

   - Executed notebooks
   - Documentation site

   Persist each box this turn: checked →
   `python -m skore_skills policy set notebooks true` (or `site`);
   unchecked → `false`. Do not leave them `null`. Do not write
   notebooks or site into JOURNAL; policy is the record.

   Same turn after persist:

   - notebooks true → load `add-python-package` for `jupytext`
     and `nbclient` (both `env route` **agent**). Do not leave
     them as `ask`. Do not convert.
   - site true → load `add-python-package` for `mkdocs-material`
     (agent), then `python -m skore_skills site init`.

   If either flag is already `true` or `false`, do not re-ask.
5. If `setup-ml-project` dispatched this turn and is in this
   session, return to it; else stop. Standalone:
   `python -m skore_skills git end-turn --stage setup`. If JSON
   `action` is `invoke`, load `persist-ml-git` when installed.
   Then load `triage-ml-task` when installed.

## Stop conditions

- Do not ask env manager, tabular library, or skore mode.
- Do not run `pixi init` / `uv init`.
- Do not env-bootstrap or editable-install. Export toolchain
  (`jupytext`, `nbclient`, `mkdocs-material`) only via
  `add-python-package` after the notebooks/site gate. Never
  `pixi add` / `uv add` from this skill.
- Do not write experiment or exploratory data analysis bodies.
- Never `git commit` here.
- Do not ask notebooks/site on an existing layout.

## Layout (CLI writes this)

```text
src/<pkg>/
experiments/
journal/
data_analysis/
data/
audit/
tests/smoke/
scratch/
reports/
```

Each directory has `README.md`.
