# Bootstrap

`setup-python-env` is bootstrap-only. Later installs go through
`add-python-package`.

## Steps

1. `python -m skore_skills env detect` + `status`.
2. Rank with JSON `recommended`: `policy.env_manager` first; else a
   unique manifest; else `provenance.manager` from the `skore`
   binary; else pixi → uv → poetry → hatch → conda → pip-venv.
   Ask when none, `ambiguous`, or `mismatch`. PATH of other tools
   is not permission.
3. Ask whether we manage the env (default yes). Persist
   `env.managed`.
4. Unmanaged: stop. Name ruff / ipython / ipykernel; do not install.
5. Managed, no (or matching) manifest: persist `env_manager`, then
   `python -m skore_skills env init --manager <manager>`. That
   command writes manager tables, the agent feature/group
   (ruff, ipython, ipykernel), and `[tool.ruff]` if missing.
6. Run `python -m skore_skills env sync --execute`, then
   `python -m skore_skills env verify --execute`. Do not retype
   `pixi install` / `uv sync`. Missing agent tools: `env route` +
   `env add --feature agent --execute`, not a second `env init`.
7. Do not create `src/`. Do not run `pixi init --format pyproject`
   if it would steal layout; `env init` writes `[tool.pixi]` itself
   and refuses when `pixi.toml` already exists.
8. Editable install waits for `has_src`. Prefer `add-python-package`
   with `env add --editable --execute`.

## What bootstrap does not install

scikit-learn, skrub, skore, pandas/polars, pytest, jupyterlab,
pyright. Pytest is added when smoke tests appear.
