---
name: add-python-package
description: >
  Add a Python dependency through the project env manager, or ask
  the user to install it when env.managed is false. Trigger when a
  workflow needs a missing import, after choose-python-library
  picks a library, or for editable install of src/<pkg>/.

  SKIP choosing between competing libraries (choose-python-library
  owns that). SKIP bootstrapping a missing manager
  (setup-python-env).

  HOW TO USE: read status.policy.env.managed and env detect. If
  managed, run the printed env add command. If unmanaged, ask;
  default is the user handles it — do not wait. Never run env add
  while managed is false.
---

# Add Python Package

The only skill that knows `python -m skore_skills env add`. Callers
must not splice manager commands themselves.

## Sequence

1. `python -m skore_skills status` and `env detect`.
2. If `policy.env.managed` is null: env is unresolved. Say so and
   stop (or send the user to setup/triage). Do not bootstrap here.
3. If `managed` is true: print-only

   ```bash
   python -m skore_skills env add [--feature agent] <packages>
   ```

   then run the printed command. Hatch: follow the edit hint; do
   not invent `pip install`.
4. If `managed` is false: **do not** run `env add` (the CLI also
   refuses). Still ask with two options:

   1. **I will handle it** (default) — name the package(s) and the
      manager-specific command (`env add` print-only is allowed as
      a hint). Do not wait; return to the caller.
   2. **Please install this now** — show the same command, wait
      until the user confirms it is done, then return. Still do
      not execute the install.

## Routes

- Runtime libraries (sklearn, skrub, skore, pandas, pytest, …) →
  default (`env add pkg`). Pytest stays on default so
  `pixi run pytest` works without `-e agent`.
- ruff / ipython / ipykernel → `--feature agent` / `--group agent`.
- Ambiguous extras (optuna, mlflow, …) → ask G-ENV-SCOPE: default
  vs a new named feature.
- Editable workspace package once `has_src` is true: pixi in
  pyproject uses `[tool.pixi.pypi-dependencies] <pkg> = { path = ".", editable = true }`
  (or `pixi add --pypi "<pkg> @ ."`). Never `pip install -e .` in a
  pixi project.

Forbidden substitutes stay in the CLI (`python-stack.json`).

Return when the import is available, when the user confirmed they
installed it, or when they chose to handle it themselves.
