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

  HOW TO USE: read status.policy.env.managed, env detect, and
  env route. If managed, env add --execute (or --editable). If
  unmanaged, ask; default is the user handles it — do not wait.
  Never --execute while managed is false.
---

# Add Python Package

The only skill that knows `python -m skore_skills env add`. Callers
must not splice manager commands themselves.

## Sequence

1. `python -m skore_skills status` and `env detect`.
2. If `policy.env.managed` is null: env is unresolved. Say so and
   stop (or send the user to setup/triage). Do not bootstrap here.
3. If this turn is the workspace package and `has_src` is true:

   ```bash
   python -m skore_skills env add --editable --execute
   ```

   when `managed` is true. Never `pip install -e .` in a pixi
   project. If `has_src` is false, stop and send the caller to
   `setup-workspace`.
4. Else `python -m skore_skills env route <pkg>`. Then:

   - `scope` `default` → `env add --execute <pkg>`
   - `scope` `agent` → `env add --feature agent --execute <pkg>`
   - `scope` `ask` → G-ENV-SCOPE, then `env add` with the chosen
     `--feature` / `--group`
   - refuse → stop; do not install

   When `managed` is true, always pass `--execute`. Never paste
   `pixi add` / `uv add` / `pip install` from memory.
5. If `managed` is false: **do not** run `env add --execute` (the
   CLI also refuses). Still ask with two options:

   1. **I will handle it** (default) — name the package(s) and
      print-only `env add` as a hint. Do not wait; return.
   2. **Please install this now** — show the same command, wait
      until the user confirms it is done, then return. Still do
      not `--execute`.

Forbidden substitutes stay in the CLI (`python-stack.json`).

Return when the import is available, when the user confirmed they
installed it, or when they chose to handle it themselves.
