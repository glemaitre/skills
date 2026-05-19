# CASE_06 — Reproducibility: add a feature without breaking prior

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

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

# Pre-flight (build-ml-pipeline)

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      Evidence: Prior 01_baseline.py runs successfully (workspace state)
- [x] Tabular library identified: pandas | polars
      Evidence: Assumed from 01_baseline running; not specified here
- [x] Skill(python-api) consulted for skrub symbols: none
      Evidence: n/a — no new skrub symbol introduced this turn
- [x] Skill(python-api) consulted for sklearn symbols: none
      Evidence: n/a — no new sklearn symbol introduced this turn
- [x] Source-binding pattern chosen: pre-existing in 01_baseline
      Evidence: Workspace state shows build_learner(data_dir_preview=None)
- [x] X-marker placement decided: pre-existing in 01_baseline
      Evidence: Workspace state; no topology change for calendar features
- [x] Per history-dependent feature step: n/a — calendar features are stateless
- [x] Layer 1 audit: n/a — calendar features append after mark_as_X
- [x] Preview value handling decided: pre-existing
      Evidence: data_dir_preview parameter already in place
- [x] split_kwargs at the X marker decided: pre-existing
      Evidence: No change to X marker for 02
- [x] Smoke test wired: pre-existing
      Evidence: 01_baseline has passing smoke test; 02 will extend it
```

---

## Answer

This is **Option 1 — parametrize with a default-preserving flag**. The change is small and well-scoped: calendar features are a stateless column-appending step with an obvious default.

### Edit `src/<pkg>/pipeline.py`

Add a boolean flag to `build_learner` with default `False` (preserves prior behavior):

```python
def build_learner(
    data_dir_preview: str | Path | None = None,
    *,
    include_calendar_features: bool = False,
) -> skrub.DataOp:
    """Build the learner pipeline.
    
    Parameters
    ----------
    data_dir_preview : str | Path | None, default=None
        Optional absolute path to data directory for preview.
        If None, requires "data_dir" in env-dict at fit time.
    include_calendar_features : bool, default=False
        If True, append day-of-week and hour-of-day features.
    
    Returns
    -------
    predictions : skrub.DataOp
        The tail of the pipeline (learner).
    """
    data_dir = (
        skrub.var("data_dir", value=str(data_dir_preview))
        if data_dir_preview is not None
        else skrub.var("data_dir")
    )
    data = data_dir.skb.apply_func(load_parquet)

    X = data.drop(["id", "target"], axis=1).skb.mark_as_X()
    y = data["target"].skb.mark_as_y()

    if include_calendar_features:
        X = X.skb.apply_func(add_calendar_features)

    predictions = X.skb.apply(predictor, y=y)
    return predictions.skb.make_learner()
```

### Experiment script behavior

- **`experiments/01_baseline.py`** calls `build_learner()` **unchanged** → uses default `False` → runs exactly as before.
- **`experiments/02_calendar_features.py`** calls `build_learner(..., include_calendar_features=True)` → appends the calendar step.

### Stateless step: `add_calendar_features`

Write this as a plain function (since day-of-week and hour-of-day are derived row-wise from a timestamp):

```python
def add_calendar_features(X: pd.DataFrame) -> pd.DataFrame:
    """Append day-of-week and hour-of-day features.
    
    Parameters
    ----------
    X : pd.DataFrame
        Input frame with a datetime column (name TBD based on your schema).
    
    Returns
    -------
    X_with_calendar : pd.DataFrame
        X with new columns: dow (0–6) and hour (0–23).
    """
    X = X.copy()
    # Adjust column name to match your schema
    X["dow"] = X["timestamp"].dt.dayofweek
    X["hour"] = X["timestamp"].dt.hour
    return X
```

### Smoke test

The existing smoke test for 01_baseline continues to pass unchanged (it uses the default flag). If you want to add a smoke test for 02, create a new test file that calls `build_learner(..., include_calendar_features=True)` — but this is optional; the unified smoke suite can run both experiments through the same `test_*.py` with parametrization if desired.

---

**Why Option 1?** Calendar features are appended at the end of the feature chain, the flag has a clear default (match prior shape), and `01_baseline.py` requires zero edits. Clean separation of concerns.
