---
name: setup-python-env
description: >
  Bootstrap a Python environment manager and two named envs
  (default runtime, agent tools). Detect with
  `python -m skore_skills env detect`, persist manager and
  `env.managed`, then `env init --manager`, `env sync --execute`,
  and `env verify --execute`. Does not add stage ML libraries.

  TRIGGER when bootstrapping a Python project or when no
  environment manager is recorded yet.

  SKIP adding later packages — load add-python-package.
  SKIP scaffolding src/ — that is setup-workspace.

  HOW TO USE: detect, ask managed vs user-managed, ask the
  manager when needed, then env init, env sync, env verify.
---

# Set Up Python Environment

Bootstrap only. Packages this turn: `ruff`, `ipython`, `ipykernel`.
Stage libraries go through `add-python-package`.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] env detect + status
- [ ] G-ENV-MGR: ask if none / ambiguous / mismatch; else keep recorded
- [ ] env.managed: ask (default true) and persist
- [ ] unmanaged → stop | managed → env init --manager, env sync --execute, env verify --execute
```

## Sequence

1. `python -m skore_skills env detect` and `status`.
2. **G-ENV-MGR.** Ask the manager when `env_manager` is `none`,
   `ambiguous`, or `mismatch`. Use JSON `recommended` as the ask
   order. PATH is not permission. Do not `curl | sh`.
3. Ask whether **we** manage the env (default yes). Persist
   `python -m skore_skills policy set env.managed true` or `false`.
4. Unmanaged: stop. Name ruff / ipython / ipykernel; do not init.
5. Managed: `policy set env_manager <manager>`, then

   ```bash
   python -m skore_skills env init --manager <manager>
   python -m skore_skills env sync --execute
   python -m skore_skills env verify --execute
   ```

   Do not hand-edit TOML. Do not run `pixi init`. Do not create
   `src/`. If verify reports missing agent tools, load
   `add-python-package` for ruff / ipython / ipykernel (agent
   feature) when that skill is installed, not a second `env init`.
   If `add-python-package` is not installed, name ruff / ipython /
   ipykernel and stop.

## Two environments

- **default** — project runtime, empty after bootstrap.
- **agent** — default plus ruff, ipython, ipykernel.
