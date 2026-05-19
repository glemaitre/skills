# CASE_02 — Tier 2 tabular library: pandas vs polars structured ask

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/data-science-python-stack/SKILL.md` (430 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder, fresh.
- `journal/JOURNAL.md` doesn't exist yet (no recorded
  `Workspace decisions`).]

Scaffold the workspace. Tabular regression task.
```

## Response

I'll scaffold the workspace for a tabular regression project. Before I generate any code, I need to nail down one competing-library choice: **which tabular library?**

<AskUserQuestion>
**Tabular dataframe — which will it be?**

- `pandas` (+ `pyarrow`) — established, already free via skore
- `polars` — Arrow-native, faster on large frames, stricter types

Pick one, or I'll default to `pandas`.
</AskUserQuestion>

While you answer that, here's what the scaffold will include:

1. **`journal/JOURNAL.md`** — project log with `Workspace decisions` block (where your tabular choice gets recorded)
2. **`pyproject.toml`** — pixi project config with Tier 1 stack (scikit-learn, skrub, skore, ruff, pytest) + your chosen tabular library
3. **`.gitignore`** — Python + pixi defaults
4. **`src/regression_task.py`** — skeleton: load data → split → fit skrub pipeline + sklearn regressor → evaluate with skore
5. **`tests/smoke/test_regression_baseline.py`** — smoke test that the pipeline runs and predicts at train time
6. **`ruff.toml`** — canonical linting config (numpydoc, sane defaults)

The structure will be ready for the `build-ml-pipeline`, `evaluate-ml-pipeline`, and `test-ml-pipeline` workflows.

**What's your pick on tabular?**
