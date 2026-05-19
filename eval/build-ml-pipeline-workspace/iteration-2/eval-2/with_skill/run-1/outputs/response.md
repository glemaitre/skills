# Response: 24-Hour-Ahead Time-Series Load Forecast

## Pre-flight Checklist

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable: sklearn, skrub, skore (skrub 0.9.0 confirmed)
- [x] Tabular library identified: pandas (inferred from time-series row structure)
- [x] python-api consulted for skrub symbols: var, mark_as_X (via SKILL.md references)
- [x] python-api consulted for sklearn symbols: BaseEstimator, TransformerMixin
- [x] Source-binding pattern chosen: multi-layer with predict-grid node
- [x] X-marker placement decided: on predict-grid node *before* featurization
- [x] History-dependent feature handling: target-shift is Layer 2, not Layer 1
- [x] Layer 1 audit completed: shift + drop_nulls are task-aware, not layer 1
- [x] split_kwargs: time-based ordering detected in timestamp column
```

## ⚠️ Anti-Pattern Detected

Your request describes the **"DON'T: wrapper estimator that filters NaN rows the pipeline produced"** anti-pattern (SKILL.md lines 99-119). This is the most common shape and the one the refactored skill explicitly forbids.

**Your approach (forbidden):**
```python
# DON'T: shifts + drops NaN in the loader
def load_and_shift(source_path):
    df = pd.read_csv(source_path)
    df['y'] = df['load'].shift(-24)  # target shift
    return df.dropna(subset=['y'])   # filtering rows the shift made
```

**Why it breaks:** This bakes the 24-hour horizon into Layer 1 (the loader). At predict time on fresh data, the loader would compute `.shift(-24)` with no history, producing NaN for all rows, then drop them silently. The graph doesn't fail — it just returns 0 rows, and you won't notice until evaluation.

## ✅ The Three-Layer Fix

Separate **what data exists** (Layer 1) from **which rows to predict** (Layer 2) from **how to featurize** (Layer 3):

### Layer 1: Raw History Source
```python
history_source = skrub.var("history", preview)  # raw load data
history_source = history_source.skb.apply_func(load_raw)
```

### Layer 2: Predict-Grid Node + Target Alignment
This is where shift + drop_nulls belong — as a **stateful estimator** that:
- Takes the predict-grid (which rows/times we want forecasts for)
- Aligns them against the full history (no cold-start rows lost)
- Computes the target `y` via shift
- Drops only the rows where `y` is genuinely NaN

```python
class TargetShiftAndAlign(BaseEstimator, TransformerMixin):
    def __init__(self, horizon=24):
        self.horizon = horizon

    def fit_transform(self, X, y=None):
        # X is the predict grid (rows we want answers for)
        # Add the target by backward-looking shift
        X = X.with_columns(
            y=pl.col("load").shift(-self.horizon)
        )
        # Drop only truly missing targets (forecast boundary)
        return X.drop_nulls("y")

    def transform(self, X):
        # At predict time, same alignment
        X = X.with_columns(
            y=pl.col("load").shift(-self.horizon)
        )
        return X.drop_nulls("y")

predict_grid = skrub.var("predict_grid", preview_grid)  # rows to forecast
predict_grid = predict_grid.skb.apply(
    TargetShiftAndAlign(horizon=24),
    cols=...  # or .skb.mark_as_X here if no history-dependent features follow
)
```

### Layer 3: History-Dependent Features (if any)
If you add lags or rolling windows, they reference the upstream `history_source`:

```python
def lag_24h(X, history):
    # X: the aligned grid (post-target-shift)
    # history: full history node passed as extra argument
    return X.with_columns(
        lag_24=pl.col("load").shift(24).over("region")
    )

X = predict_grid.skb.apply_func(lag_24h, history_source)
X = X.skb.mark_as_X(split_kwargs={"groups": X["region"]})
```

## Key Points

1. **Layer 1** = raw history loader only. No shifts, no drop_nulls.
2. **Layer 2** = predict-grid node + TargetShiftAndAlign estimator (stateful). This is where the shift happens and NaN rows are dropped.
3. **Layer 3** = features that reference history via `.skb.apply_func` extra arguments.
4. **mark_as_X** goes on the predict-grid node (or after Layer 2 alignment if the estimator doesn't include it).
5. **split_kwargs**: since you have timestamps and regions, wire `split_kwargs={"groups": X["region"]}` or time-based splits (ask `evaluate-ml-pipeline` for the splitter choice).

## Smoke Test Implication

The smoke test will fit on train data and predict on disjoint test data with no pre-history buffer. If your loader bakes the shift, smoke returns 0 rows at predict time and fails on the assertion. This correctly catches the anti-pattern — don't loosen the assertion; fix the topology instead.

---

**Full reference:** SKILL.md § "Late `mark_as_X` is forbidden..." (lines 75–119); also `references/layer_examples.md` § "History-dependent — early-mark with upstream reference".
