# Time-Series Load Forecast Loader

## Pre-flight checklist

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (skrub installed at 0.9.0)
- [x] Tabular library identified: pandas
      (inferred from row-wise load data with timestamp/region/load columns)
- [x] python-api consulted for skrub symbols: var, mark_as_X, mark_as_y
      Evidence: n/a — standard skrub DataOps API, stable in 0.9.x
- [x] python-api consulted for sklearn symbols: none
      Evidence: n/a — no new sklearn symbol this turn
- [x] Source-binding pattern chosen: skrub.var root on raw source
      (one source: the raw load data with timestamp, region, load columns)
- [x] X-marker placement decided: AFTER target shift and NaN drop
      (forward shift on y is cross-row; markers must come before featurization,
       but target derivation with drop belongs in Layer 2 as a stateful step)
- [x] Per history-dependent feature step: not applicable downstream
      (layer 2 only; no additional history reference needed)
- [x] Layer 1 audit: loader is pure — reads timestamp, region, load
      (external consumer would load the same, no task knowledge required)
- [x] Preview value handling: passed as optional kwarg, not literal
- [x] split_kwargs at the X marker decided: groups = region
      (region is a group identifier; temporal ordering handled by timestamp)
- [x] Smoke test wired: will be implemented per smoke-test-ml-pipeline
```

## Design

**Layer 1 (Sources):** Load the raw data (timestamp, region, load columns).

**Layer 2 (Predict-time grid + alignment):** Compute the 24-hour-ahead target via `shift(-24)` on the load column, drop rows with NaN in y, then apply `mark_as_X` and `mark_as_y`. This is a stateful operation because:
- It derives the target column (task-specific knowledge)
- It filters rows (changes the effective dataset)
- It must fit on training data only to avoid data leakage

**Layer 3 (Feature engineering):** Downstream lags, rolling statistics, or cross-row joins reference the marked X and the raw history as separate inputs.

## Recommended loader structure

```python
import pandas as pd
import skrub

def load_forecast_data(data_path_or_preview):
    """Load raw load forecast data with (timestamp, region, load)."""
    # Load from path (production) or inline preview (development)
    if isinstance(data_path_or_preview, str):
        df = pd.read_csv(data_path_or_preview)
    else:
        df = data_path_or_preview
    return df


class TargetShiftAndDropNaN(skrub.BaseEstimator, skrub.TransformerMixin):
    """Compute 24-hour-ahead target and drop NaN rows in y."""
    
    def fit(self, X, y=None):
        # Stateless fit for this step
        return self
    
    def transform(self, X):
        """
        X: DataFrame with 'load' column
        Returns: X with 'y' appended; rows with NaN in 'y' dropped.
        """
        X = X.copy()
        X['y'] = X['load'].shift(-24)  # 24-hour-ahead target
        X = X.dropna(subset=['y'])      # Drop rows with missing target
        return X


# Build the learner
def build_learner(data_preview=None):
    raw_source = skrub.var(
        "raw_load_data",
        value=data_preview,
    ).skb.apply_func(load_forecast_data)
    
    # Layer 2: Target shift and drop NaN
    data_with_target = (
        raw_source
        .skb.apply(TargetShiftAndDropNaN())
    )
    
    # Mark X (features) and y (target)
    X = (
        data_with_target
        .drop(['y', 'load'])  # Drop target and the source column
        .skb.mark_as_X(
            split_kwargs={'groups': data_with_target['region']}
        )
    )
    
    y = (
        data_with_target['y']
        .skb.mark_as_y()
    )
    
    # Layer 3: Feature engineering (if needed) goes here
    # e.g., X.skb.apply_func(add_lags, data_with_target, ...)
    
    return skrub.SkrubLearner(X=X, y=y, estimator=None)  # estimator TBD
```

## Key decisions

1. **Cross-row placement:** The `shift(-24)` creates a forward-looking target (cross-row dependency), so target derivation happens *before* marking X. The `TargetShiftAndDropNaN` estimator encapsulates this, preserving the three-layer boundary.

2. **Stateful target step:** Although shift-and-drop sounds simple, it:
   - Derives a task-specific quantity (the label for a forecasting task)
   - Changes dataset size (drop NaN rows)
   - Must not see test data during fit
   → Implemented as a stateful transformer, not a plain function.

3. **Group metadata:** Region is passed as `split_kwargs={'groups': ...}` at the X marker so that cross-validation can stratify by region (e.g., StratifiedGroupKFold) if needed downstream.

4. **Preview flexibility:** The loader accepts a `data_preview` kwarg for interactive iteration; production fit/cross-validate call `build_learner()` with no argument (preview=None).

5. **Next step:** Layer 3 feature steps (lags, rolling windows, external regressors) attach downstream on the X branch, taking the raw history as an additional argument to compute time-lagged features without cold-start leakage.

## Testing

Smoke test (per `smoke-test-ml-pipeline`) will:
- Fit on a train subset with history deep enough for the shift
- Predict on a disjoint test subset
- Assert row count = predict-grid size (no silent NaN losses)
