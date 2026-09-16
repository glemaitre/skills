---
name: setup-python-env
description: >
  Bootstrap a Python environment manager and two named envs
  (default runtime, agent tools). Detect with
  `python -m skore_skills env detect`, persist manager and
  `env.managed`, then run `env init --manager`. Does not add
  stage ML libraries.

  TRIGGER when bootstrapping a Python project or when no
  environment manager is recorded yet.

  SKIP adding packages after bootstrap — load add-python-package.
  SKIP non-Python tools.

  HOW TO USE: detect, ask managed vs user-managed, ask the
  manager when needed, then `env init`. Narrate every choice.
---

# Set Up Python Environment

Bootstrap only. Name every choice this turn: manager,
`env.managed`, two-env layout, packages `ruff` / `ipython` /
`ipykernel`. Do not install sklearn, skrub, skore, pandas,
jupyterlab, or pyright.

Adding a later dependency is `add-python-package`, not this skill.

## Stop conditions

- **Wrong-manager install is forbidden.** Never `pip install` in a
  pixi project.
- **No silent bootstrap.** If no manager is detected, ask. Recommend
  from `env detect` `recommended`: policy `env_manager`, then a
  unique manifest, then `provenance.manager` (`skore` install
  path), then pixi → uv → poetry → hatch → conda → pip-venv.
  PATH of other tools is not permission. Do not run `curl | sh`.
- **No silent ambiguity.** If `ambiguous` is true, ask which
  manifest is the project manager. If `mismatch` is true, ask:
  recorded policy disagrees with the unique manifest.
- **User opt-out.** If the user manages the env, persist
  `env.managed` false and **stop**. Do not `env init` or `env add`.
  Name ruff / ipython / ipykernel as tools they may want later.
- **Do not hand-edit manager TOML.** `env init` is the only writer
  of manager tables. Do not create `pixi.toml` when pixi can live in
  pyproject. Do not create `src/`.
- **A missing layout is a status fact.** When `has_src` is false,
  editable install is pending. Do not scaffold here.

## Pre-flight

```
- [ ] Detection: python -m skore_skills env detect
- [ ] G-ENV-MGR: <manager> | ask
- [ ] env.managed: true | false | ask (default true)
- [ ] Command: python -m skore_skills env init --manager <name>
- [ ] Narrated: default + agent; ruff, ipython, ipykernel
```

## Sequence

1. `python -m skore_skills env detect` and `status` (policy).
2. Rank managers from `recommended`. Ask when none, `ambiguous`,
   or `mismatch`.
3. Ask whether **we** manage the env (default yes). Persist
   `python -m skore_skills policy set env.managed true` or `false`.
4. If unmanaged: stop after detection. Do not init.
5. If managed: `policy set env_manager <manager>`, then

   ```bash
   python -m skore_skills env init --manager <manager>
   ```

   Review the printed `next:` command (install/sync). Do not invent
   TOML. No sklearn/skrub/skore/pandas/jupyterlab/pyright.
6. After workspace exists (`has_src`), editable install is
   `add-python-package` (or the dispatcher), not a second bootstrap
   mode here.

## Two environments

- **default** — project runtime. Empty after bootstrap.
- **agent** — default plus ruff, ipython, ipykernel. Interpreter for
  `cells run` and ruff.

uv/poetry: default dependencies plus an `agent` group. Hatch/conda:
two envs. No `dev` env, no `lsp` env, no pyright.

Ruff config is `[tool.ruff]` in `pyproject.toml`. Leftover
`ruff.toml` is still valid. Run style with
`python -m skore_skills style`.

## References

- `references/bootstrap.md`
- `references/composition_model.md`
- `references/install_commands_anatomy.md`
- `references/per_manager_footguns.md`
