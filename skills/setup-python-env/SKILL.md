---
name: setup-python-env
description: >
  Bootstrap a Python environment manager and three named envs
  (default runtime, agent tools, composed dev). Detect with
  `python -m skore_skills env detect`, persist manager and
  `env.managed`, then `env init --manager`, `env sync --execute`,
  install plain Skore, and `env verify --execute`. Does not add
  other stage ML libraries.

  TRIGGER when the user asks for the env manager, pixi, uv, or a
  Python environment, or when no environment manager is recorded
  yet.

  SKIP adding later packages — load add-python-package.
  SKIP scaffolding src/ — that is setup-workspace.

  HOW TO USE: detect, ask managed vs user-managed, ask the
  manager when needed, then env init, env sync, add plain Skore,
  and env verify.
---

# Set Up Python Environment

Bootstrap only. Direct packages this turn: `ruff`, `ipython`,
`ipykernel`, and plain `skore`. Skore supplies `skore-skills` as a
mandatory dependency. Other stage libraries go through
`add-python-package`.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] env detect + status
- [ ] G-ENV-MGR: ask if none / ambiguous / mismatch; else keep recorded
- [ ] env.managed: ask (default true) and persist
- [ ] unmanaged → stop | managed → env init, env sync, add-skore local, env verify
```

## Sequence

1. `python -m skore_skills env detect` and `status`.
2. **G-ENV-MGR.** Ask the manager when `env_manager` is `none`,
   `ambiguous`, or `mismatch`. Use JSON `recommended` as the ask
   order. PATH is not permission. Do not `curl | sh`.
3. Ask whether **we** manage the env (default yes). Persist
   `python -m skore_skills policy set env.managed true` or `false`.
4. Unmanaged: stop. Name ruff / ipython / ipykernel / skore; do not init.
5. Managed: `policy set env_manager <manager>`, then

   ```bash
   python -m skore_skills env init --manager <manager>
   python -m skore_skills env sync --execute
   python -m skore_skills env add-skore --mode local --execute
   python -m skore_skills env verify --execute
   ```

   Do not hand-edit TOML. Do not run `pixi init`. Do not create
   `src/`. Plain Skore is the sole early stage-library exception; do
   not ask G-SKORE-MODE here. Later, `add-python-package` upgrades it
   for Hub or MLflow after that gate resolves.
   If verify reports missing `skore` or `skore_skills`, rerun
   `env add-skore --mode local --execute`; never add `skore-skills`
   directly. If verify reports missing agent tools, load
   `add-python-package` for ruff / ipython / ipykernel (agent feature)
   when that skill is installed, not a second `env init`.
   If `add-python-package` is not installed, name ruff / ipython /
   ipykernel and stop.

## Three environments

- **default** — project runtime; bootstrap installs plain `skore`,
  which supplies `skore-skills`.
- **agent** — ruff, ipython, ipykernel.
- **dev** — default + agent. Every later `python -m skore_skills`
  command uses this composed environment; `env verify --execute`
  must pass before other skills run.
