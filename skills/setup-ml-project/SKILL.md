---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Dispatch the
  environment, workspace, and git actions in order; skip any of them
  that is not installed; do not duplicate their work.
---

# Set Up ML Project

This meta skill owns ordering only. Run
`python -m skore_skills status` first and read `skills`:

- `false` — the action is not installed. Skip it, say so in one
  line, and continue with the next step.
- `true` — load it.
- `null` — install state is unknown. Load it only if it is in this
  session; if it is not there, skip it like `false`.

Never reproduce a skipped skill's procedure from memory.

1. `setup-python-env` — **bootstrap only**: resolve G-ENV-MGR,
   persist it with `python -m skore_skills policy set env_manager
   <manager>`, and run the manager's `init`. No ML stack, no
   editable install yet.
2. `setup-workspace` — detect/glue or scaffold after the package
   and skore-mode gates. A manager manifest without `src/<pkg>/` is
   still a scaffold target: `python -m skore_skills scaffold
   --package <pkg>` keeps an existing `pyproject.toml`.
3. `setup-python-env` again, only when `status.has_src` is true —
   editable install of `src/<pkg>/` plus `env add` for the
   libraries the workspace gates resolved.
4. `setup-git` — initialize version control with the user's
   first-commit decision. Persist autocommit (`on`/`off`) once via
   `policy set`. Later stages run
   `python -m skore_skills git end-turn` then `persist-ml-git`.

Run `python -m skore_skills status` again after setup to surface
missing pieces and persist policy facts. Stop when setup is a safe
scaffold: load `triage-ml-task` when it is installed, otherwise
report the remaining gaps and stop. Do not start EDA or a pipeline.

## Stop conditions

- Never silently pick package name, tabular library, env manager, or
  skore mode.
- Never run `pip install` in a pixi project.
- Never commit without asking.
- Never run a skipped skill's steps yourself, and never fail the
  whole setup because one action is missing.
- Do not write pipeline or experiment bodies; setup stops at a safe
  scaffold.

This is a deliberately small dispatcher pending joint review.
