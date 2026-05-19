# CASE_06 — The `project.get` lookup-shape trap

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-api/SKILL.md` (568 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `skore.Project` instance bound to `project`, mode `local`.
- The baseline experiment was run last week; its report is in the
  Project under key `"01_baseline"`.]

`project.get("01_baseline")` is raising `KeyError`. The report must be
missing — let's re-run `experiments/01_baseline.py` to put it back.
```

## Response

**Stop.** Before re-running, consult `project.summarize()` first — the `KeyError` on a **key** lookup almost certainly means the **lookup shape is wrong**, not that the report is missing.

Let me check the Project state:

```python
"""Audit: Project.summarize() to list all reports by id + key."""
from skore import Project

project = Project(workspace="current", mode="local")
summary = project.summarize()
print(summary)
print("\n---\n")
print(f"Columns: {summary.columns.tolist()}")
print(f"Index (id): {summary.index.tolist()}")
```

Save as `scratch/2025-01-15_001_audit_project.py`, run with `pixi run python scratch/2025-01-15_001_audit_project.py`.

**Why:** `skore.Project.get(...)` resolves by **id** (the DataFrame index), not by user-facing **key** (a column). The call signature is `get(id)`, not `get(key)`. A failed `get(key="01_baseline")` or `get("01_baseline")` does **not** mean the report is missing — it means you're using the wrong accessor.

Once `summarize()` lands, scan the `key` column for `"01_baseline"`. You'll find the row; read its `id` value (left column); call `project.get(id=<that_id>)` instead.

**If you find the row:** Re-running is unnecessary. The report exists; the lookup just needed the id.

**If you don't find the row:** *Then* the report is genuinely missing, and re-running is the right move.

Paste the `summarize()` output and I'll confirm which case you're in.
