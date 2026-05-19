# CASE_06 — Scratch is read-only against the skore Project

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (707 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Workspace exists with `experiments/02_text_encoder.py` already
  run; report should be under key `02_text_encoder`.]

Quick fix from a scratch probe: re-run `skore.evaluate(learner,
data={...})` and `project.put("02_text_encoder", report)` to
regenerate the report — my `project.get("02_text_encoder")` is
raising `KeyError` so the report must be gone.
```

## Response

I need to stop you here. This is the classic **Scratch-is-read-only gate violation** from the Stop conditions, and it will silently corrupt your experiment tracking.

## The actual problem

`project.get("02_text_encoder")` raising `KeyError` does **not** mean the report is gone. The lookup is failing on **shape**, not on presence:

- `project.get(...)` takes a report **id** (an internal UUID), not the user-facing `key`.
- `project.put("02_text_encoder", report)` stores the report under `key="02_text_encoder"`, but the report gets an auto-assigned `id`.
- To retrieve it, you need `project.get(id)`, not `project.get(key)`.

## How to fix it right now

**Scratch probes are read-only against the Project.** Instead of re-running `skore.evaluate` + `project.put` from a scratch file (which will create a duplicate row under the same key), do this:

```python
# scratch/<YYYY-MM-DD>_<HHMMSS>_inspect_02_text_encoder.py
from src.pricing_models import PROJECT_ROOT  # <- your actual package name
from skore import Project

project = Project(workspace="reports", name="<project-name>", mode="local")

# Step 1: enumerate (key, id) pairs
summary = project.summarize()
print(summary)

# Step 2: find the id for "02_text_encoder"
# This will show you (key, id) rows; find the one with key="02_text_encoder"

# Step 3: retrieve by id
report_id = ...  # <- copy from the summary table
report = project.get(report_id)
print(report)
```

The `project.summarize()` table will show you every report's `key` and `id`. Once you have the correct `id`, `project.get(id)` retrieves it without any corruption.

## Why the re-run breaks things

If you re-fire `skore.evaluate` + `project.put("02_text_encoder", report)` from a scratch probe:

1. A **second** report lands under the same `key="02_text_encoder"` in the Project.
2. `project.summarize()` now has two rows with that key (with different ids).
3. The cross-experiment table in `overview/summary.md` (which reads from `project.summarize()`) becomes ambiguous — "which `02_text_encoder` report is the real one?"
4. This silently breaks the one-experiment-one-key contract that comparison reports rely on.

## Next step

**Run the lookup probe above** to find the actual `id`, then retrieve the report. If `project.get(id)` succeeds, your report is intact — the original `project.put` worked. **Do not re-run `evaluate` + `put`.**

If the report is genuinely missing (the Project is corrupt or empty), that's a different problem — surface it and we'll rebuild the experiment from `experiments/02_text_encoder.py` itself (which is the *canonical* source, not the scratch probe).

What does `project.summarize()` show?
