# Smoke Test Row-Count Mismatch

I cannot loosen the hard assertion to `>= 0.95 * n_predict_grid_rows`. Here's why:

## The Row-Count Check Is the Whole Point

The hard assertion (`len(predictions) == n_predict_grid_rows`) is the **structural-correctness check** the smoke test exists to catch. It is binary: pass or fail. Loosening it silently reintroduces the bug you're trying to detect.

## Your Pipeline Has a Cross-Row Problem

The 24-row gap you're seeing is **not** a spurious mismatch — it's a diagnostic signal. You have:

- **Pipeline shape**: lag features (cross-row dependencies)
- **Predict-env size**: 744 rows
- **Predictions returned**: 720 rows
- **Gap size**: 24 rows = the lag window (168h or similar)

This is exactly the failure mode the smoke test is designed to catch: **cold-start rows are being dropped** at predict time. When the pipeline computes backward lags on the predict env (which carries only the rows you want predictions for, with no pre-history buffer), the first 24 rows fall into the cold-start zone and get dropped by a pre-marker `drop_nulls` or by the model's NaN intolerance.

## What to Do Instead

Route back to **`build-ml-pipeline`**. Your X-marker is landing too late in the DAG. The fix:

1. **Audit the X-marker placement**: The marker should land *before* any history-dependent feature steps (lags, rolling windows, joins with upstream history).
2. **Check history-source binding**: History-dependent features must take an upstream history node as an additional `apply_func` argument, not compute the history per-slice from the predict env alone.
3. **Verify the predict-grid alignment**: Once corrected, the pipeline will produce the full 744 predictions — and the smoke test will pass trivially.

The design note's failure semantics (from § "Failure semantics") are clear: a hard-assertion failure is a **pipeline-shape problem**, not a metric problem. Don't tune the model, don't add a wrapper, don't loosen the assertion. **Fix the shape.**

Once you've corrected the X-marker placement, the smoke test will pass without any changes to the assertion.
