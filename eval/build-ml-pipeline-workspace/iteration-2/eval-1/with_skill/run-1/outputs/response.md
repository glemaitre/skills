# Pipeline Setup Response

## Pre-flight Check

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per workspace state: skrub, scikit-learn, skore are installed)
- [x] Tabular library identified: pandas
      (mixed-type DataFrame, IID flat table, no cross-row features)
- [ ] python-api consulted for skrub symbols: none
      (n/a — skrub.var, SkrubLearner documented in skill; no new symbols)
- [ ] python-api consulted for sklearn symbols: none
      (StandardScaler, Ridge are baseline estimators; symbols will be confirmed in code)
- [x] Source-binding pattern chosen: skrub.var("data", preview)
      (single flat-table source, IID case → var root with optional preview parameter)
- [x] X-marker placement decided: directly on the loaded source frame
      (IID flat table, no cross-row features → mark early on the loaded data)
- [ ] Per history-dependent feature step: n/a
      (no lag, rolling window, target shift, or cross-row join in scope)
- [x] Layer 1 audit: no loading + featurization fusion
      (loader is pure: data → frame, no task-specific transformations upstream of mark_as_X)
- [x] Preview value handling: build_pipeline exposes preview as optional kwarg
      (None by default for production; caller can pass absolute path for interactive preview)
- [ ] split_kwargs at the X marker: none
      (IID case; no group structure, temporal ordering, or repeated measures mentioned)
- [x] Smoke test requirement noted for later
      (per smoke-test-ml-pipeline skill; simple IID fit + predict on disjoint slices)
```

## Direction: Redirect to Skrub DataOps

Your request asks for a bare `sklearn.Pipeline` with `StandardScaler` and `Ridge`. **This is out of scope for `build-ml-pipeline`.** The skill mandates:

> **Rule 1 — Skrub DataOps is the pipeline entry point**
> Declare the pipeline as a skrub DataOps graph rooted at one or more `skrub.var(...)` calls — **not** as a bare `sklearn.Pipeline`.

This is a structural design choice, not a preference:
- A bare `sklearn.Pipeline` couples the data source to the pipeline declaration, breaking predict-time replay against fresh sources.
- A skrub DataOps graph separates **Layer 1** (data sources) from **Layer 2** (the predict grid) from **Layer 3** (featurization), enabling:
  - Validation of the topology via smoke tests (fit on one slice, predict on a disjoint slice without pre-history buffer)
  - Replay on new data without editing code
  - Proper handling of cross-row features (lags, rolling windows, target shifts) when the task evolves

## What `build_pipeline()` Should Contain

For an IID regression task, declare a **skrub SkrubLearner** using the three-layer model:

1. **Layer 1 (Sources):** `skrub.var("data", preview)` loads the raw DataFrame
2. **Layer 2 (X marker):** `.skb.mark_as_X()` on the loaded frame (IID case)
3. **Layer 3 (Learner tail):** `.skb.apply(StandardScaler()).skb.apply(Ridge())` as stateful estimators

**Structural outline:**

```python
def build_pipeline(data_preview=None):
    """
    Build a baseline regression pipeline using StandardScaler and Ridge.
    
    Parameters
    ----------
    data_preview : str, optional
        Absolute path to a preview DataFrame for interactive inspection.
        None for production use.
    
    Returns
    -------
    learner : SkrubLearner
        A skrub DataOps graph (not a bare sklearn Pipeline) that encodes
        the data source → preprocessing → prediction topology.
    """
    from skrub import var
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    
    # Layer 1: Source binding
    # var("data", preview) loads the input; preview is used only for interactive exploration
    data = var("data", preview=data_preview)
    
    # Layer 2: Predict-time grid marker (IID case — mark directly on loaded frame)
    X = data.skb.mark_as_X()
    
    # Layer 3: Preprocessing + estimator (both are stateful, applied in sequence)
    learner = X.skb.apply(StandardScaler()).skb.apply(Ridge())
    
    return learner
```

The key differences from a bare `sklearn.Pipeline`:
- **Input:** environment dict `{"data": path_or_frame}`, not (X, y) tuple
- **Output:** a `SkrubLearner` that delays evaluation, enabling preview and replay
- **Evaluation contract:** pair with `skore.evaluate(learner, data={"data": ...}, splitter=...)` (see `evaluate-ml-pipeline` skill)

## File Location

Write this function to:

```
src/<pkg>/pipeline.py
```

where `<pkg>` is the package name (inferred from workspace structure).

## Next Steps

1. **Consult `python-api`** for exact import paths and method signatures of `skrub.var`, `.skb.mark_as_X()`, `.skb.apply()`, and confirm `StandardScaler` / `Ridge` are from the correct modules
2. **Write `src/<pkg>/pipeline.py`** with `build_pipeline(data_preview=None)` following the three-layer structure above
3. **Write `tests/smoke/test_baseline_pipeline.py`** per `smoke-test-ml-pipeline` skill — validates topology by fitting on one slice and predicting on a disjoint slice
4. **Invoke `python-code-style`** to check docstrings and formatting
5. **Verify the pipeline** by fitting with `skore.evaluate(...)` and checking the smoke test passes

The baseline is intentionally minimal — only StandardScaler + Ridge applied as stateful estimators. Once the topology is correct and smoke passes, you can extend Layer 3 with feature engineering without structural debt.
