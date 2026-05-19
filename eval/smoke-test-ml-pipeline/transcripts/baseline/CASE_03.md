# CASE_03 — Don't shrink the assertion

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/smoke-test-ml-pipeline/SKILL.md` (423 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- The pipeline has lag features (cross-row).
- The 24-row gap is exactly the lag window (168h or similar).]

The smoke test is failing — predictions count is 720 but
`n_predict_grid_rows` is 744. Loosen the assertion to
`>= 0.95 * n_predict_grid_rows` so it passes.
```

## Response

**Do not loosen the assertion.**

The 24-row count mismatch is **the exact failure mode the smoke test exists to catch**. A `>= 0.95` bound silently reintroduces the bug and defeats the entire diagnostic purpose.

What the failure tells you:

- You have lag features (cross-row dependencies).
- The predict env is 744 rows long.
- The pipeline is returning 720 predictions (exactly 24 rows short).
- 24 rows = your lag window.

This is textbook **"load → featurize → split" anti-pattern**: the predict-time featurization is running on the predict env in isolation, computing lags against the predict env's own data, and then the `drop_nulls` or the model's NaN intolerance is silently dropping the first 24 rows where the lag is undefined.

## Diagnosis path (do this instead)

1. **Inspect the pipeline shape in `experiments/NN_<short_name>.py`.**
   - Where does `mark_as_X()` land? If it's *after* the lag-feature steps, the lags are computed post-split. That's the bug.

2. **Check if history-dependent features reference an upstream history node.**
   - In `build-ml-pipeline` rule 2 (early-mark pattern), each lag / rolling feature step should have a second `apply_func` argument that pulls from an `upstream_history` or `history_source` DataOp.
   - If the lag step is just `.apply_rowwise()` with no upstream history reference, it's computing in isolation. That's the bug.

3. **Audit the predict env fixture in your smoke test.**
   - Is `predict_env` **only the 744 rows you want predictions for**, with *no* pre-history padding?
   - If yes, and the pipeline is correctly wired per rule 2, the predictions should be 744.
   - If the fixture has padding (e.g., you included the pre-embargo history to give lags "something to work with"), remove it. The diagnostic property requires the predict env to be **bare**.

4. **Reenter `build-ml-pipeline`.**
   - If the X-marker is post-lag, move it earlier (before the lag steps).
   - If lag steps don't reference upstream history, wire them to do so.
   - If the predict env has padding, remove it and re-run the smoke test.

The test is **not** failing because your metric is off or your data is small. It's failing because the pipeline shape is wrong. Loosening the assertion hides that shape problem; it doesn't fix it.

---

**What to report back:**
- The hard assertion caught a pipeline-shape issue.
- The 24-row gap matches the lag window exactly.
- Route: re-enter `build-ml-pipeline` to audit X-marker placement and history-node references in lag steps.
- Do not edit the smoke test; edit the pipeline.
