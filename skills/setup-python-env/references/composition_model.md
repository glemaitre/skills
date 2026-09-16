# Two-environment composition

Pixi features are routing, not four user-facing envs:

```toml
[tool.pixi.feature.agent.dependencies]
ruff = "*"
ipython = "*"
ipykernel = "*"

[tool.pixi.environments]
default = { features = ["default"], solve-group = "default" }
agent   = { features = ["default", "agent"], solve-group = "default" }
```

- **default** — runtime. Empty after bootstrap; stage libraries
  arrive via `add-python-package`.
- **agent** — `default + agent`. Used for `cells run` and ruff.

There is no `dev` env and no `lsp` env. Optional extras (optuna, …)
ask G-ENV-SCOPE: `default` vs a new named feature. New features do
not need an LSP growth rule.

uv/poetry: `[project.dependencies]` plus `[dependency-groups] agent`.
Hatch: `[tool.hatch.envs.default]` and `[tool.hatch.envs.agent]`.
Conda: `environment.yml` and `environment-agent.yml`.
