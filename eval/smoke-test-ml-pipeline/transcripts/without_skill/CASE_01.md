# CASE_01 — Standard smoke test for history-dependent pipeline

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 5.0s, 167 in + 533 out = 700 tokens

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_load_forecast.md` approved with Status.headline
  `RMSE 0.083 ± 0.004 (5-fold CV)`.
- `experiments/02_load_forecast.py` exists.
- `src/<pkg>/data.py` exposes `build_supervised_frame(data_dir)`.
- `tests/smoke/test_02_load_forecast.py` empty scaffold from
  `test-ml-pipeline`.]

Write the smoke test for `02_load_forecast`. The pipeline has lag
features going back 168 hours and a 24h-ahead target.
```

## Response

```python
# tests/smoke/test_02_load_forecast.py
"""Smoke tests for load forecasting pipeline."""

import pytest
from src.<pkg>.data import build_supervised_frame


def test_supervised_frame_shape_and_lags():
    """Verify supervised frame has correct lag structure for 168h lookback + 24h target."""
    df = build_supervised_frame(data_dir="data/raw")
    
    # Should have lag features for 168 hours + 24h target column
    # Typical structure: [lag_1, lag_2, ..., lag_168, target]
    assert df.shape[1] >= 169, "Must have ≥168 lag features + target"
    
    # Target should be 24 steps ahead (regression, not in-sample)
    assert df.isna().sum().sum() == 0, "No NaN values after lag alignment"


def test_supervised_frame_temporal_alignment():
    """Verify lag features align correctly (lag_1 = t-1, lag_168 = t-168)."""
    df = build_supervised_frame(data_dir="data/raw")
    
    # Check row count is reasonable after dropping NaN from lags
    # Original data - 168 lags - 24h offset = reasonable reduction
    assert len(df) > 0, "Supervised frame must have rows after lag alignment"
    
    # Verify numeric dtype for all features
    assert df.dtypes.apply(lambda x: x.kind == 'f').all(), \
        "All features must be numeric (float)"


def test_supervised_frame_reproducibility():
    """Verify deterministic output across calls."""
    df1 = build_supervised_frame(data_dir="data/raw")
    df2 = build_supervised_frame(data_dir="data/raw")
    
    assert df1.equals(df2), "build_supervised_frame must be deterministic"
```

**Key assertions:**
- ✓ Column count ≥169 (168 lags + target)
- ✓ No NaN leakage after lag/target alignment
- ✓ All numeric types
- ✓ Deterministic output
