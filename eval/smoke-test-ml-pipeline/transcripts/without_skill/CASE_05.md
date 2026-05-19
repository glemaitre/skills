# CASE_05 — No `skore` import in smoke test

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 1.5s, 97 in + 116 out = 213 tokens

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Smoke test currently has a hardcoded `CV_MEAN_MAE = 0.083` from
  the design note.
- skore is in the env.]

Add `from skore import Project` to the smoke test so we can read
the CV mean from `project.summarize()` instead of hardcoding it.
```

## Response

# Add Project import to smoke test

```python
from skore import Project
```

Then update the smoke test to read the CV mean from the project:

```python
project = Project()
summary = project.summarize()
CV_MEAN_MAE = summary['cv_mean_mae']  # or however it's keyed in summarize()
```

This replaces the hardcoded `CV_MEAN_MAE = 0.083` and makes the test dynamic based on actual project results.
