# CASE_01 — Tier 1 mandatory libs at project start

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/data-science-python-stack/SKILL.md` (430 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder.]

Starting a fresh ML project. What's the mandatory stack?
```

## Response

# Mandatory Stack for Your ML Project

Here's what installs at project start:

1. **`scikit-learn`** — tabular ML algorithms, preprocessing, model selection
2. **`skrub`** — data cleaning + feature engineering layer (wraps dataframe ops in sklearn-compatible graphs)
3. **`skore`** — model evaluation, cross-validation reports, and experiment tracking via the Project API
4. **`ruff`** — lint + format (replaces black / isort / flake8)
5. **`pytest`** — test runner for the smoke-test gate

All five go into the same environment feature so `pixi run` commands work without extra activation.

---

## Before you install: one decision gate

The stack has **five Tier 1 libraries** (above — non-negotiable) and **one Tier 2 competing-library job that fires now**: which tabular dataframe library?

**Your options:**
- **`pandas` (+ `pyarrow`)** — established, already pulled in transitively by `skore`, so effectively "free"
- **`polars`** — Arrow-native, faster on large frames, stricter types; requires explicit install

Which would you prefer for this project?

Once you pick, I'll generate the install command via `python-env-manager` (detects whether the project uses pixi / uv / poetry / hatch / conda / pip+venv and produces the right syntax).
