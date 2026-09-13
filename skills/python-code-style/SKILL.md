---
name: python-code-style
description: >
  Owns Python code style for this stack: ruff for lint + format,
  numpydoc for docstrings. Places `ruff.toml` from the bundled
  template when missing, runs `python -m skore_skills style` on
  Python files just generated or edited, and rewrites leftover
  template/workflow comments into concise problem-specific prose.

  TRIGGER after creating or editing Python; on fresh scaffold with
  no root `ruff.toml`; or when asked about lint, format, docstrings,
  black, isort, flake8, pydocstyle, or pylint.

  SKIP non-Python work, vendored/generated code, and untouched files.

  HOW TO USE: read Stop conditions, emit Pre-flight, then run
  `python -m skore_skills style <touched paths>`. Manual only: never
  configure a PostToolUse / PreToolUse hook.
---

# Python Code Style

Ruff is the stack's formatter, import sorter, and linter. Run it
manually on files touched this turn.

## Stop conditions

- **No hooks.** Refuse PostToolUse / PreToolUse configuration. If
  the user still wants automation, redirect to `update-config`;
  default remains manual.
- **No substitutes.** Do not install or configure black, isort,
  flake8, pydocstyle, or pylint. Ruff covers those jobs.
- **Touched paths only.** Do not lint the whole repository or fix
  unrelated warnings. Surface warning codes from untouched files
  and ask whether to handle them as a separate task.
- **One retry.** Run the CLI; fix remaining issues once; if the same
  issue survives, stop and report diagnostics. No third cycle.
- **No memory-authored config.** Copy `templates/ruff.toml`
  verbatim. If its content is supplied in the prompt, use that exact
  content.
- Do not suppress warnings unless explicitly asked.
- Comments and docstrings describe the data-science problem, not
  skill names, gates, runners, or scaffolding mechanics.

## Pre-flight

```
- [ ] Touched Python paths: <paths only>
- [ ] ruff.toml: present | copy bundled template verbatim
- [ ] Command: python -m skore_skills style <paths>
- [ ] Unrelated diagnostics: none | <codes>, ask separately
```

## Style pass

Run:

```bash
python -m skore_skills style <path> [<path> ...]
```

The CLI runs Ruff's fix pass then formatter using the workspace
configuration. It returns non-zero when issues remain. Do not repeat
the Ruff command anatomy in plans or run black/isort separately.

Default paths when none are provided are `src/`, `experiments/`,
`audit/`, `data/eda.py`, and top-level `*.py`; prefer explicit
touched paths to avoid widening scope. Exclude `.pixi/`, `.venv/`,
`node_modules/`, vendored and generated code, and other user-owned
data files.

When an untouched file has diagnostics:

```
In scope: <touched.py>
python -m skore_skills style <touched.py>

Out of scope: <untouched.py> — <codes>
Ask: address <untouched.py> as a separate task?
```

## Initial `ruff.toml`

If the project is scaffolded but root `ruff.toml` is missing:

1. Read `.agents/skills/python-code-style/templates/ruff.toml`
   this turn (or use exact prompt-supplied content).
2. Write it verbatim to `<project-root>/ruff.toml`.
3. Verify with `pixi run ruff check --show-settings .`.

Do not fold it into `pyproject.toml` or enrich it from memory.

## Documentation contract

Public functions use numpydoc:

```python
def predict_price(X, model):
    """Predict prices for feature rows.

    Parameters
    ----------
    X : ndarray of shape (n_samples, n_features)
        Feature matrix.
    model : sklearn.base.BaseEstimator
        Fitted estimator.

    Returns
    -------
    ndarray of shape (n_samples,)
        Predicted prices.
    """
```

- Imperative one-line summary, then a blank line.
- `Parameters` and `Returns` for public functions.
- Put array shape in the type slot.
- Rewrite template/workflow comments into problem language.
- Private helpers may omit docstrings under the default rules.

## Companion skills

- `python-env-manager` installs Ruff with the detected manager if
  missing; never fall back to `pip install` in a pixi workspace.
- `organize-ml-workspace` creates paths referenced by the bundled
  config.
- `data-science-python-stack` owns Ruff as Tier 1.
