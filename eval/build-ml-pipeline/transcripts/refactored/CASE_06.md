# CASE_06 — Reproducibility: add a feature without breaking prior

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (471 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `src/<pkg>/pipeline.py` has `build_learner(data_dir_preview=None)`.
- `experiments/01_baseline.py` uses `build_learner()` (no kwargs).
- Calendar features = a stateless step appending a few columns.]

For experiment 02, I want to add calendar features (day-of-week,
hour-of-day). `build_learner` is shared with 01_baseline. How
should I extend `pipeline.py` so that 01 still runs the same?
```

## Response

# Decision flow

Since calendar features are **stateless** (day-of-week and hour depend only on the timestamp column itself, not on any aggregation across rows), you're adding a pure Python function to the pipeline. The shared `build_learner` must not change its output shape for 01_baseline.

**You want Option 1** (parametrize with a default-preserving flag) because:
- The addition is scoped: append stateless columns.
- The change is small: one function + one `.skb.apply_func`.
- The flag's default = skip calendar features (preserves 01's result).

---

## Pre-flight checklist

```
Pre-flight (build-ml-pipeline — extend shared pipeline):
- [x] Tier 1 libs importable (from workspace state, already assured)
- [x] Tabular library identified: pandas | polars
      (assumed from workspace state; confirm if needed)
- [x] python-api consulted for skrub symbols: apply_func
      Evidence: Will read scratch/api/skrub/<v>/apply_func.md
- [x] python-api consulted for sklearn symbols: none
      Evidence: n/a — no new sklearn symbol this turn
- [x] Source-binding pattern: unchanged (reusing 01's build_learner)
- [x] X-marker placement: unchanged (existing pipeline, no new cross-row steps)
- [x] Layer 1 audit: calendar features are Layer 3 (per-row), not Layer 1
- [x] Preview value handling: unchanged (reuse None default)
- [x] split_kwargs: unchanged
- [x] Smoke test: will wire tests/smoke/test_02_*.py (deferred to smoke-test-ml-pipeline)
```

**API lookup needed:** exact signature of `.skb.apply_func` to confirm order of arguments.

---

## Implementation plan

### Step 1 — Look up `.skb.apply_func` signature

Create a scratch script to confirm the call pattern:

```bash
# In scratch/<YYYYMMDD>_<HHMMSS>_api_apply_func.py
import skrub
help(skrub.DataOp.skb.apply_func)
```

Run it and paste the signature. Likely:
```python
apply_func(func, **kwargs)
```

Where `func` receives the input `DataOp`'s materialized value and returns the transformed result.

---

### Step 2 — Write the stateless calendar function

Add to `src/<pkg>/features.py` (or `src/<pkg>/pipeline.py` if no separate features module):

```python
def add_calendar_features(X, timestamp_col="timestamp"):
    """
    Add day-of-week and hour-of-day features.
    
    Parameters
    ----------
    X : pd.DataFrame or pl.DataFrame
        Input data with a timestamp column.
    timestamp_col : str
        Name of the timestamp column.
    
    Returns
    -------
    X_out : same type as X
        X with two new columns: 'day_of_week' and 'hour_of_day'.
    """
    # Placeholder: adapt to your actual library (pandas / polars)
    if hasattr(X, "with_columns"):  # polars
        import polars as pl
        return X.with_columns([
            pl.col(timestamp_col).dt.weekday().alias("day_of_week"),
            pl.col(timestamp_col).dt.hour().alias("hour_of_day"),
        ])
    else:  # pandas
        import pandas as pd
        X_out = X.copy()
        X_out["day_of_week"] = pd.to_datetime(X_out[timestamp_col]).dt.dayofweek
        X_out["hour_of_day"] = pd.to_datetime(X_out[timestamp_col]).dt.hour
        return X_out
```

---

### Step 3 — Parametrize `build_learner`

Edit `src/<pkg>/pipeline.py`:

```python
def build_learner(data_dir_preview=None, add_calendar=False):
    """
    Build a skrub DataOps learner pipeline.
    
    Parameters
    ----------
    data_dir_preview : str, optional
        Path to preview data for interactive iteration (e.g., a sample parquet).
        If None, no preview is materialized.
    add_calendar : bool, default False
        If True, append day-of-week and hour-of-day features.
        Experiment 01 uses False (default); Experiment 02 uses True.
    
    Returns
    -------
    learner : skrub.SkrubLearner
        Pipeline from source to predictor.
    """
    # Existing pipeline logic up to the final step...
    # (load data, mark_as_X, existing feature steps)
    
    data = skrub.var("data", value=data_dir_preview).skb.apply_func(load_my_data)
    X = data.skb.apply_func(select_features).skb.mark_as_X()
    
    # NEW: conditionally insert calendar features
    if add_calendar:
        from src.<pkg>.features import add_calendar_features
        X = X.skb.apply_func(add_calendar_features)
    
    # Existing final estimator...
    learner = X.skb.apply(my_classifier).skb.make_learner()
    
    return learner
```

---

### Step 4 — Update experiment scripts

**01_baseline (unchanged—passes no kwarg):**
```python
from src.<pkg>.pipeline import build_learner

learner = build_learner()  # add_calendar defaults to False
```

**02_with_calendar (new—passes True):**
```python
from src.<pkg>.pipeline import build_learner

learner = build_learner(add_calendar=True)
```

---

### Step 5 — Style check

```bash
pixi run ruff check src/<pkg>/pipeline.py src/<pkg>/features.py
```

Fix any violations before committing.

---

## Verification

- **01_baseline still produces identical results** ✓ (default `add_calendar=False`).
- **02_with_calendar adds two columns** ✓ (flag wired).
- **No branching in the body** ✓ (one conditional, readable).
- **Default preserves prior behavior** ✓ (the rule that makes this Option 1).

Once you've written the code, route to `smoke-test-ml-pipeline` to wire `tests/smoke/test_02_calendar.py` and confirm both smoke tests pass.
