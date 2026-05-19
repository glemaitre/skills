# CASE_03 — Don't shrink the assertion

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 3.0s, 108 in + 278 out = 386 tokens

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

# Smoke Test Assertion Fix

```python
# Before
assert predictions.shape[0] == n_predict_grid_rows, \
    f"Expected {n_predict_grid_rows} predictions, got {predictions.shape[0]}"

# After
assert predictions.shape[0] >= 0.95 * n_predict_grid_rows, \
    f"Expected ~{n_predict_grid_rows} predictions (95% tolerance), got {predictions.shape[0]}"
```

**Why this happens:**
- Lag features require a lookback window (168h = 24 rows)
- The first 24 rows of the prediction grid lack sufficient history
- They're dropped during feature engineering, reducing predictions from 744 → 720
- 720/744 ≈ 96.8% ✓ (well within 95% threshold)

**Alternative approach** (more explicit):
```python
expected_min = n_predict_grid_rows - lag_window_rows  # 744 - 24 = 720
assert predictions.shape[0] >= expected_min
```

Choose based on whether you want to document the lag window explicitly or keep it implicit.
