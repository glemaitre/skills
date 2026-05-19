# CASE_05 — No `skore` import in smoke test

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/smoke-test-ml-pipeline/SKILL.md` (423 lines)

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

I need to stop you here — this request directly violates the Stop conditions of the smoke-test-ml-pipeline skill.

From the skill description, **Stop condition 5**:

> **Do not import `skore`** (or any other tracking / reporting
> library) in the test file. The smoke test must be runnable in
> any environment that can `import skrub` + `import sklearn` —
> the skore Project is a side artifact, not a test dependency.

And the companion note in the standard pytest shape:

> CV_MAE_MEAN is hardcoded at the top of the file from
> `journal/NN_<short_name>.md` § Status.headline. The smoke test
> uses only the predicting package's API (skrub/sklearn) — **no
> skore import, so it runs anywhere skrub does.**

### Why this rule exists

The smoke test is a **pre-flight check for pipeline correctness**, not a metric-tracking artifact. It must be:

1. **Portable** — runnable in any environment with skrub + sklearn, even if the skore Project doesn't exist or is corrupted.
2. **Deterministic** — no runtime dependency on the state of `project.summarize()`. If the project gets re-run or archived, the smoke test still works.
3. **Fail-safe** — if skore is missing or the project is inaccessible, the test should still run (with the hardcoded baseline), not crash on an import.

### The right approach

Keep the hardcoded `CV_MEAN_MAE = 0.083` and update it **by hand** when the design note's Status.headline number changes. Add a comment pointing to the design note:

```python
# Soft-assertion baseline from journal/NN_<short_name>.md § Status.headline
CV_MEAN_MAE = 0.083
```

This is the intended design — the smoke test is intentionally *decoupled* from the skore Project so it can run anywhere the predicting package does.

If you need to automate the baseline sync, that's a separate script (maybe a CI step) that reads the design note and updates the smoke-test constant — but the test itself must not import skore.
