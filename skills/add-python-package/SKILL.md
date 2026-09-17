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
  env route. Classify this turn first (editable | add-skore |
  named package). If managed, env add --execute (or --editable).
  If unmanaged, ask; default is the user handles it — do not wait.
  Never --execute while managed is false.
---

# Add Python Package

The only skill that knows `python -m skore_skills env add`. Callers
must not splice manager commands themselves.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status + env detect
- [ ] env.managed: null → stop | false → ask, no --execute | true → continue
- [ ] classify: editable | add-skore | env route then env add
```

## Sequence

1. `python -m skore_skills status` and `env detect`.
2. If `policy.env.managed` is null: env is unresolved. Say so and
   stop. Do not bootstrap here. Do not load `setup-python-env` by
   catalog id unless the user asked for env setup.
3. Classify this turn **before** adding anything:

   - **Editable** only if the user asked to install the workspace
     package, or `setup-ml-project` selected that box. `has_src`
     true is not enough.
   - **Skore** if the package is Skore.
   - **Named package** otherwise (`skrub`, pandas, …). Never
     `--editable` for a named dependency.

4. If `managed` is false: **do not** `--execute`. Ask with two
   options:

   1. **I will handle it** (default) — name the package(s) and
      print-only `env add` (or `env add --editable`, or
      `env add-skore --mode <mode>`). Do not wait; return.
   2. **Please install this now** — show the same command, wait
      until the user confirms it is done, then return.

5. If this turn is editable and `has_src` is true:

   ```bash
   python -m skore_skills env add --editable --execute
   ```

   Never `pip install -e .` in a pixi project. If `has_src` is
   false, stop. Name `setup-workspace` only if it is installed.
6. If the package is Skore, read the persisted `policy.skore_mode`
   and run:

   ```bash
   python -m skore_skills env add-skore --mode <mode> --execute
   ```

   If the mode is unset, return to `evaluate-ml-pipeline`. Do not
   spell `skore[...]` or pick conda vs PyPI yourself. See
   `add-python-package/references/skore_variant.md`.
7. Else `python -m skore_skills env route <pkg>`. Then:

   - `scope` `default` → `env add --execute <pkg>`
   - `scope` `agent` → `env add --feature agent --execute <pkg>`
   - `scope` `ask` → G-ENV-SCOPE, then `env add` with the chosen
     `--feature` / `--group`
   - refuse → stop; do not install

   Always pass `--execute`. Never paste `pixi add` / `uv add` /
   `pip install` from memory.

Forbidden substitutes stay in the CLI (`python-stack.json`).

Return when the import is available, when the user confirmed they
installed it, or when they chose to handle it themselves.

## References

- `references/skore_variant.md`
