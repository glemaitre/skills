# Install commands — by manager

Bootstrap writes files via `env init`. Later adds go through
`python -m skore_skills env add [--feature|--group] <packages>`.

| Manager | Config | Bootstrap follow-up | Runtime add | Agent add |
|---|---|---|---|---|
| pixi | `[tool.pixi.*]` in pyproject | `pixi install -e agent` | `pixi add pkg` | `pixi add --feature agent pkg` |
| uv | `[project]` + PEP 735 groups | `uv sync --group agent` | `uv add pkg` | `uv add --group agent pkg` |
| poetry | PEP 621 + PEP 735 groups | `poetry install --with agent` | `poetry add pkg` | `poetry add --group agent pkg` |
| hatch | `[project]` + `[tool.hatch.envs.agent]` | `hatch env create agent` | edit pyproject | edit `envs.agent` |
| conda | `environment.yml` + `environment-agent.yml` | `conda env create -f environment-agent.yml` | `conda install -c conda-forge pkg` | same, in the agent env |
| pip-venv | pyproject groups and/or `requirements.txt` | create `.venv` then pip | `pip install pkg` | same venv or agent extra |

Known routes for `add-python-package`: runtime → default; ruff /
ipython / ipykernel → agent; pytest → default so `pixi run pytest`
works without `-e agent`. Ambiguous extras (optuna, mlflow) ask
G-ENV-SCOPE: default vs a new named feature.
