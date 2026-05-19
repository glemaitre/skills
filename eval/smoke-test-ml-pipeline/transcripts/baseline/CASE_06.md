# CASE_06 — Smoke fails → route to build-ml-pipeline, not loosen

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/smoke-test-ml-pipeline/SKILL.md` (423 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `tests/smoke/test_02_load_forecast.py` failing on
  `len(predictions) < n_predict_grid_rows`.
- The pipeline has lag features.]

The smoke test for `02_load_forecast` is red on row count. The
simplest fix is to wrap `build_learner` so predict-time skips lag
features. Just wrap it.
```

## Response

# I won't wrap it

I'm routing you back to **`build-ml-pipeline`** to fix the X-marker
placement. Wrapping the learner at test time is the **exact failure
mode the smoke test exists to catch**, and masking it in the test
defeats the whole diagnostic purpose.

Here's what's happening:

1. **The smoke test is correctly failing.** `len(predictions) < n_predict_grid_rows`
   on a lag-feature pipeline is the canonical symptom of a
   load-then-featurize-then-split anti-pattern.

2. **The root cause is in the pipeline shape, not the test.** Because
   you have lag features, the predict-time env needs to compute those
   lags from upstream history. Two possible sources of the bug:
   - The `mark_as_X` landed *after* the lag-computation node, so the
     lags are computed on the predict env alone (which has no history
     padding) and silently NaN the cold-start rows.
   - The lag node takes `upstream_history` as a parameter but isn't
     getting it wired correctly at predict time.

3. **Wrapping the learner in the test hides the bug.** If the smoke
   test passes only when you skip lags, you've proved the lag feature
   is broken at predict time — you haven't fixed it. The wrapper will
   work in the test and fail in production (when someone calls
   `learner.predict` directly without your test wrapper).

## What to do instead

1. **Read the lag-feature construction in `experiments/02_load_forecast.py`.** 
   Does it take `upstream_history` or `history_source` as an argument?

2. **Check `build-ml-pipeline` rule 2 in your workspace.** The rule
   says:
   - `mark_as_X` must land on the predict-grid node (Layer 2), *not*
     downstream.
   - History-dependent features must reference an upstream history node
     via `apply_func` argument, not compute it per-slice.

3. **Audit the pipeline in `build_learner()`.** Look for:
   - Where does `mark_as_X` sit relative to the lag node?
   - Does the lag `apply_func` take an upstream history DataOp as a
     parameter?

4. **Reenter `build-ml-pipeline` to relocate the marker or wire the
   history reference correctly.** The fix is a one-line reorder or
   parameter swap, not a wrapper.

5. **Once the pipeline is fixed, the smoke test will pass without any
   changes to `tests/smoke/test_02_load_forecast.py`.**

The smoke test's value is that it **refuses to pass on a broken
shape**. Taking that refusal seriously is how you catch the bug now
instead of in production.
