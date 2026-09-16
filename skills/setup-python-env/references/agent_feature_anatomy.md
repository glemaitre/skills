# Agent env (not LSP)

The agent environment is `default` plus ruff, ipython, and
ipykernel. It exists for `python -m skore_skills cells run` and
`python -m skore_skills style`.

There is no pyright, no `pyrightconfig.json`, and no `lsp` env.
Harness editors may ship their own language servers; this stack
does not install or configure them.

Bootstrap writes the agent tables through
`python -m skore_skills env init --manager <name>`. Later adds use
`add-python-package` with `--feature agent` only for those three
tools (or ruff if it was skipped).
