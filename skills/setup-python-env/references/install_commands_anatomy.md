# Install commands

Do not invent manager argv. Print or run:

- Bootstrap files: `python -m skore_skills env init --manager <name>`
- Install/sync: `python -m skore_skills env sync --execute`
- Scope: `python -m skore_skills env route <pkg>` then
  `env add [--feature agent] --execute`
- Skore: `python -m skore_skills env add-skore --mode <mode> --execute`
- Editable `src/<pkg>/`: `python -m skore_skills env add --editable --execute`
- Agent tools present: `python -m skore_skills env verify --execute`

`env sync` / `env add` already encode pixi, uv, poetry, hatch, conda
(`-n` from YAML), and pip-venv. Hatch add writes pyproject.
`env add-skore` selects conda-forge `skore` for pixi/conda and
PyPI requirements (including mode extras) for other managers.

`env route` `scope`:

- `agent` — ruff, ipython, ipykernel (`--feature agent`)
- `default` — stage and chosen runtime libraries (pytest on default)
- `ask` — extras (optuna, mlflow, jupyterlab, …) → G-ENV-SCOPE
- refuse — forbidden substitutes (CLI exit 1)
