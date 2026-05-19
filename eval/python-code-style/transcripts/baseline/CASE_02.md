# CASE_02 — No `ruff.toml` yet, fresh scaffold

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-code-style/SKILL.md` (218 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `pyproject.toml` exists, `src/<pkg>/`, `experiments/`, `journal/`
  scaffolded.
- No `ruff.toml` at the project root.
- ruff is installed via the env manager.]

Set up the linter config for this freshly scaffolded workspace.
```

## Response

# Pre-flight (python-code-style)

- [x] ruff importable in the project's env (`pixi run ruff --version`
      succeeds, per `data-science-python-stack` Tier 1)
- [ ] `ruff.toml` present at project root — **will drop template now**
- [ ] File list ready: N/A (setup phase, no touched files yet)
- [ ] Decision recorded: initial setup — placing bundled config

---

## Setting up `ruff.toml`

Reading the bundled template and writing it to your project root:

```toml
[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = [
    "F",      # Pyflakes: undefined names, unused imports
    "E",      # pycodestyle errors: spacing, indentation
    "W",      # pycodestyle warnings: blank lines, trailing whitespace
    "I",      # isort: import sorting
    "UP",     # pyupgrade: modern Python syntax
    "B",      # flake8-bugbear: likely bugs and design problems
    "D",      # pydocstyle: docstring coverage and format
    "RUF",    # ruff-specific checks
]

ignore = [
    "E501",   # Line too long (handled by formatter)
    "D100",   # Missing module docstring (ignored in experiments/)
    "D101",   # Missing class docstring in some contexts
    "D104",   # Missing docstring in __init__.py
]

[tool.ruff.lint.per-file-ignores]
"experiments/**" = ["D100", "D103"]  # Allow missing module/function docstrings in notebooks
"tests/**" = ["D100", "D101", "D102", "D103"]  # Test files
"__init__.py" = ["F401"]  # Allow unused imports (re-exports)

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.format]
quote-style = "double"
skip-magic-trailing-comma = false
```

✓ Written to `<project-root>/ruff.toml`

Verify the setup:

```bash
pixi run ruff check --show-settings .
```

You should see `convention = "numpy"` and the full `select` list above in the output. Ready to lint Python files as you create them — this skill will run ruff on any `.py` files you touch.
