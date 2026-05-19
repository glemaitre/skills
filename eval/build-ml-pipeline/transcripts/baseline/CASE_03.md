# CASE_03 — History-dependent late `mark_as_X` trap

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- skrub installed at 0.9.0.
- The user is in early baseline construction.]

Time-series load forecast. Each row = (timestamp, region, load).
I want a 24-hour-ahead forecast. Write the loader so it computes
`y = load.shift(-24)` then drops the rows with `NaN` in `y`, and
we'll do `mark_as_X` on the result.
```

## Response

# STOP — Layer 1 violation detected

I need to surface a structural issue **before** writing any code.

You're describing the **late-`mark_as_X` anti-pattern** flagged in the
Stop conditions. Here's why it breaks:

## The problem

Your loader computes `y = load.shift(-24)` and `drop_nulls(y)` *before*
the marker. This means:

1. The loader bakes in the assumption: *"we want to predict load 24
   hours ahead"* — a task-specific decision, not a property of the raw
   data source.
2. When the next experiment wants to add a **lagged-load feature**
   (e.g., `load.shift(-1)` to see "what was the load 1 hour ago?"),
   that feature function looks at the raw history — but your loader has
   already dropped rows with NaN in `y`, creating a structural hole:
   - Row at `t=100`: the target shift wants `t=124`, but
   - Row at `t=1`: the lag feature wants `t=0`, which doesn't exist
   because the loader pre-filtered to rows with valid 24-hour targets.

   The graph is now mis-shaped for composition.

3. The smoke test will pass (the downstream graph is IID, so no
   cross-row reaches fail), but you've silently built debt that
   surfaces when you try to layer features on top.

## The fix: three-layer structure

**Layer 1 (raw source):** load the hourly data as-is, no shifts, no
drops.

**Layer 2 (alignment + mark):** given a *predict grid* (which
`(timestamp, region)` pairs do we want forecasts for?), join the
targets onto those rows. This is where `shift(-24)` and the `drop_nulls`
go — after you've named what "the rows we want predictions for" are.

**Layer 3 (features after mark):** lagged features, rolling stats, etc.,
all referencing the upstream raw history via an additional argument.

### Concrete structure

```python
def build_learner(predict_grid_preview=None, history_source_preview=None):
    # Layer 1: raw history (no shifts, no drops)
    history_source = (
        skrub.var("history_source", value=history_source_preview)
        if history_source_preview is not None
        else skrub.var("history_source")
    )
    history = history_source.skb.apply_func(load_history)

    # Layer 2: predict grid (timestamp/region pairs we forecast for)
    predict_grid = (
        skrub.var("predict_grid", value=predict_grid_preview)
        if predict_grid_preview is not None
        else skrub.var("predict_grid")
    )

    # Align: join targets onto predict_grid rows, drop NaN in y
    aligned = skrub.as_data_op(
        {"predict_grid": predict_grid, "history": history}
    ).skb.apply(TargetAligner())
    
    X = aligned["X"].skb.mark_as_X()
    y = aligned["y"].skb.mark_as_y()

    # Layer 3: features after mark_as_X
    # The lag feature takes X and the upstream history;
    # it joins real values onto every row in the predict grid
    X = X.skb.apply_func(add_lagged_load, history)
    
    predictions = X.skb.apply(predictor, y=y)
    return predictions.skb.make_learner()
```

### What is `TargetAligner()`?

A small stateful estimator (fits on training, transforms on test):

```python
from sklearn.base import BaseEstimator, TransformerMixin

class TargetAligner(BaseEstimator, TransformerMixin):
    """Align predict grid + history into (X, y) for 24-hour-ahead forecast."""

    def fit(self, data, y=None):
        # data = {"predict_grid": grid_op, "history": history_op}
        # The .skb.apply(...) call evaluates these to frames
        self.is_fitted_ = True
        return self

    def transform(self, data):
        grid = data["predict_grid"]  # (timestamp, region, ...)
        history = data["history"]    # (timestamp, region, load, ...)
        
        # Join history onto grid to get targets
        # Pseudocode; exact join depends on your schema
        merged = grid.join(
            history[["timestamp", "region", "load"]],
            on=["timestamp", "region"],
            how="left"
        )
        
        # Compute target: load 24 hours ahead
        merged = merged.with_columns(
            y=pl.col("load").shift(-24)
        )
        merged = merged.drop_nulls("y")
        
        X = merged.drop("y")
        y = merged["y"]
        
        return {"X": X, "y": y}
```

(Adjust the frame library to match your workspace choice — pandas
vs. polars — and the exact join/column logic to your schema.)

---

## Before I write the actual code

I need to ask you three structural questions:

1. **What describes the predict grid?** Is it:
   - A time range (`start` / `end` timestamps, and all regions)?
   - An explicit list of `(timestamp, region)` tuples?
   - Something else?

2. **Do you have both sources available at experiment time?** (raw
   history file + a predict-grid descriptor), or is the grid derived
   from the history itself (e.g., "all rows with timestamp ≥
   T-lookback")?

3. **Will there be lagged/rolling features downstream?** (This question
   determines whether the three-layer shape is essential now or nice-to-have
   for future flexibility.)

Once you answer, I'll write the full loader + aligner + Layer-3 feature
template, wire the preview parameters correctly, and run the
pre-flight checklist.
