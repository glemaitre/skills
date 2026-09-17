# setup-ml-project eval

---

## CASE_01 — Full project setup

**User prompt:**
> Set up this empty folder for a tabular ML project.

**Assumed workspace state:**
- Empty folder; no manager or package name selected.
- `python -m skore_skills status` reports every `skills` entry
  `true`.

**Must do:**
- Emit the Pre-flight then load the child skills (do not stop
  after listing boxes).
- Load `setup-python-env`, then `setup-workspace`, then
  `add-python-package` (editable only), then `setup-git`.
- Leave manager, `env.managed`, and package-name questions to
  those skills. Do not ask G-TABULAR or G-SKORE-MODE.

**Must NOT do:**
- Scaffold or ask for the package name before the environment
  manager turn.
- Ask G-TABULAR or G-SKORE-MODE, or persist `tabular` /
  `skore_mode`, during setup.
- Run `pip install`.
- Commit without asking.
- Write a runnable baseline experiment.
- Run `git push`.

---

## CASE_02 — Editable install waits for the layout

**User prompt:**
> Continue the setup.

**Assumed workspace state:**
- `python -m skore_skills status` reports `env_manager: pixi`,
  `policy.env_manager: pixi`, `has_src: false`, `git: false`.
- `pixi.toml` and a `pixi init` `pyproject.toml` exist; no `src/`.
- Every `skills` entry is `true`.

**Must do:**
- Read `status` first and treat the manager as already resolved.
- Load `setup-workspace` next (`has_src` is false).
- Schedule `add-python-package` for the editable install only
  after `has_src` is true. Do not install sklearn/skrub/skore.
- Finish with `setup-git`.

**Must NOT do:**
- Re-ask G-ENV-MGR.
- Pass `--force` to `scaffold`.
- Wire the editable install before the layout exists.

---

## CASE_03 — Git skill not installed

**User prompt:**
> Bootstrap this project for me.

**Assumed workspace state:**
- Empty folder.
- `python -m skore_skills status` reports `skills`:
  `setup-python-env: true`, `setup-workspace: true`,
  `setup-git: false`, `choose-python-library: true`,
  `persist-ml-git: false`, `triage-ml-task: true`.

**Must do:**
- Dispatch the environment and workspace steps normally.
- State in one line that git setup is skipped because `setup-git`
  is not installed.
- Finish the rest of setup rather than stopping at the missing
  skill.

**Must NOT do:**
- Run `git init`, `git add`, or `git commit` to cover for the
  missing skill.
- Invent the `setup-git` procedure from memory.
- Treat the missing skill as an error that aborts setup.
