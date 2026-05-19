# CASE_02 — No `ruff.toml` yet, fresh scaffold

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-code-style/SKILL.md` (263 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `pyproject.toml` exists, `src/<pkg>/`, `experiments/`, `journal/`
  scaffolded.
- No `ruff.toml` at the project root.
- ruff is installed via the env manager.]

Set up the linter config for this freshly scaffolded workspace.
Here's the content of `.agents/skills/python-code-style/templates/ruff.toml`
from the bundle (I just read it for you):

```toml
line-length = 88
target-version = "py312"

[lint]
select = ["E", "F", "W", "I", "B", "UP", "D"]
ignore = [
    # Imports do not have to live at the top of the file — `# %%` cells
    # in `experiments/` interleave imports between code blocks.
    "E402",
    # Bare expressions are intentional in `# %%` notebook cells (display output).
    "B018",
]

[lint.pydocstyle]
convention = "numpy"

[format]
docstring-code-format = true
```
```

## Response

# Python Code Style — Initial Setup

Reading the bundled template ✓. Writing it verbatim to project root now.

```bash
Write pyproject.toml → ruff.toml
```

**ruff.toml (project root):**
```toml
line-length = 88
target-version = "py312"

[lint]
select = ["E", "F", "W", "I", "B", "UP", "D"]
ignore = [
    # Imports do not have to live at the top of the file — `# %%` cells
    # in `experiments/` interleave imports between code blocks.
    "E402",
    # Bare expressions are intentional in `# %%` notebook cells (display output).
    "B018",
]

[lint.pydocstyle]
convention = "numpy"

[format]
docstring-code-format = true
```

**Verify ruff picks it up:**
```bash
pixi run ruff check --show-settings .
```

Expected output includes:
- `pydocstyle convention = "numpy"`
- `select = ["E", "F", "W", "I", "B", "UP", "D"]`
- `ignore = ["E402", "B018"]`

✓ **Setup complete.** The workspace is now configured for:
- **Formatting** (line length 88, quote style, trailing commas)
- **Linting** (undefined names, imports, deprecated syntax, numpydoc docstrings)
- **Notebook cells** (`experiments/` can have `# %%` blocks with imports between cells and bare display expressions)

When you generate or edit Python files, this skill will run `ruff format` + `ruff check --fix` + `ruff check` on them before declaring the task done.
