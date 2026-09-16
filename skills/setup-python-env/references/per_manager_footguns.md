# Per-manager footguns (no LSP)

## pixi

Do not write both `pixi.toml` and `[tool.pixi]` in pyproject — pixi
prefers `pixi.toml` if both exist. `env init --manager pixi` refuses
when `pixi.toml` is present. Prefer `[tool.pixi.*]` in pyproject.

## uv

Agent tools: `uv add --group agent`. Runtime: `uv add` into
`[project.dependencies]`. Resync with `uv sync --group agent`.

## poetry

Use PEP 621 `[project]` plus PEP 735 `[dependency-groups]`.
`poetry add --group agent` for ruff/ipython/ipykernel.

## hatch

No universal add command. `env add` prints an edit hint. Agent env
is `[tool.hatch.envs.agent]`. Do not treat `[tool.hatch.build]` as
an env-manager signal.

## conda / mamba

Cannot live in pyproject. `environment.yml` (runtime) and
`environment-agent.yml` (tools).

## pip + venv

Prefer `[project.dependencies]` + `[dependency-groups]` when a
pyproject exists. `requirements.txt` only if that is already the
project contract.
