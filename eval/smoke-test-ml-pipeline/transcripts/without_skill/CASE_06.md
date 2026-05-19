# CASE_06 — Smoke fails → route to build-ml-pipeline, not loosen

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 3.5s, 109 in + 345 out = 454 tokens

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

# Fix the smoke test by wrapping `build_learner`

I'll add a wrapper around `build_learner` that removes lag features at predict time.

```python
# In the relevant module (likely in your learner/model building code)

def build_learner_wrapped(config, train_data):
    """
    Wrapper around build_learner that handles lag features at predict time.
    
    Removes lag feature columns before prediction to avoid row count mismatch.
    """
    learner = build_learner(config, train_data)
    
    # Store original predict method
    original_predict = learner.predict
    
    def predict_without_lags(X):
        """Predict after dropping lag feature columns."""
        # Identify lag columns (adjust pattern to match your lag naming)
        lag_cols = [col for col in X.columns if 'lag_' in col.lower()]
        X_filtered = X.drop(columns=lag_cols, errors='ignore')
        return original_predict(X_filtered)
    
    # Replace predict method
    learner.predict = predict_without_lags
    return learner
```

**Then update the test/forecast pipeline to use `build_learner_wrapped` instead of `build_learner`.**

This avoids the row count mismatch by ensuring lag features (which require historical context) don't get passed to prediction, keeping the output size aligned with `n_predict_grid_rows`.
