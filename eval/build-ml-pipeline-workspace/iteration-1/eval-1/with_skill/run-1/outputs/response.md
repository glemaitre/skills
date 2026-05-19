# Pipeline Setup Response

## Pre-flight Check

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (skrub, scikit-learn, skore are installed per workspace state)
- [x] Tabular library identified: pandas
      (mixed-type DataFrame, no cross-row features → IID tabular case)
- [ ] python-api consulted for skrub symbols: none
      (n/a — no new symbols needed; skrub.var is documented in the skill)
- [ ] python-api consulted for sklearn symbols: none
      (n/a — Standard baseline; symbols will be confirmed in the code)
- [x] Source-binding pattern chosen: skrub.var("data", preview)
      (single flat table, IID case → var root with preview parameter)
- [x] X-marker placement decided: directly on the loaded source frame
      (IID flat table with no cross-row features)
- [x] Layer 1 audit: no history-dependent steps upstream of X marker
      (pure loading, no shifts/windows/joins)
- [x] Preview value handling: build_pipeline exposes preview as optional kwarg
      (None by default for production; caller supplies path for interactive use)
- [x] split_kwargs at the X marker: none
      (IID case; no group structure or temporal ordering mentioned)
- [x] Smoke test requirement noted for later
      (after pipeline is declared, per smoke-test-ml-pipeline skill)
```

## Direction: Redirect to Skrub DataOps

Your request asks for a bare `sklearn.Pipeline` with `StandardScaler` and `Ridge`. **This is out of scope for `build-ml-pipeline`.** The skill mandates:

> **Rule 1 — Skrub DataOps is the pipeline entry point**
> Declare the pipeline as a skrub DataOps graph rooted at one or more `skrub.var(...)` calls — **not** as a bare `sklearn.Pipeline`.

This is a structural design choice, not a preference:
- A bare `sklearn.Pipeline` couples the data source (shape, loading path) to the pipeline declaration, breaking predict-time replay against fresh sources.
- A skrub DataOps graph separates **Layer 1** (data sources) from **Layer 2** (the predict grid) from **Layer 3** (featurization), enabling:
  - Testing on disjoint train/test splits without leakage
  - Replaying the same pipeline on new data without editing code
  - Proper smoke-test validation of the topology

## What `build_pipeline()` Should Contain

Instead of a bare sklearn Pipeline, declare a **skrub SkrubLearner** using the three-layer model:

1. **Layer 1 (Sources):** `skrub.var("data", preview)` loads the raw DataFrame
2. **Layer 2 (X marker):** `.skb.mark_as_X()` on the loaded frame (IID case, no feature steps yet)
3. **Layer 3 (Learner tail):** `.skb.apply(Ridge())` with StandardScaler as a preprocessing step inside

**The structure will look like:**

```python
def build_pipeline(data_preview=None):
    from skrub import var, SkrubLearner
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    
    # Layer 1: Source
    data = var("data", preview=data_preview)
    
    # Layer 2: Mark the predict grid (IID flat table)
    X = data.skb.mark_as_X()
    
    # Layer 3: Feature engineering → learner
    learner = X.skb.apply(StandardScaler()).skb.apply(Ridge())
    
    return learner
```

The difference is:
- **Input:** environment dict with `{"data": dataframe_or_path}`, not (X, y) tuples
- **Output:** a `SkrubLearner` that handles source binding and lazy execution
- **Smoke test:** validates topology by fitting on a portion and predicting on a disjoint portion

## Next Steps

1. **Consult `python-api`** for exact signatures of `skrub.var`, `SkrubLearner`, and the `.skb` API methods
2. **Write `src/<pkg>/pipeline.py`** with the `build_pipeline(data_preview=None)` function following the three-layer pattern above
3. **Write `tests/smoke/test_baseline_pipeline.py`** (see `smoke-test-ml-pipeline` skill) with a simple fit + predict on disjoint data slices
4. **Run style checks** via `python-code-style` skill to validate docstrings and formatting

The baseline is intentionally simple — only StandardScaler + Ridge, applied as stateful estimators in sequence. Once the topology is correct and smoke passes, you can add feature engineering steps in Layer 3 without risk of structural debt.
