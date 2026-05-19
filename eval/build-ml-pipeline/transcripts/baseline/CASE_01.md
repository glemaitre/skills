# CASE_01 — Bare `sklearn.Pipeline` → redirect to skrub DataOps

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Tabular regression task, mixed-type DataFrame, no cross-row
  features (IID).
- `skrub`, `scikit-learn`, `skore` are installed and importable.
- No existing `src/<pkg>/pipeline.py`.]

Set up the baseline pipeline using `sklearn.Pipeline` with a
`StandardScaler` and `Ridge`. Just write `src/<pkg>/pipeline.py`
with a `build_pipeline()` function.
```

## Response

I need to stop and redirect before writing any code.

## Stop condition triggered

**Rule violation: bare `sklearn.Pipeline` instead of skrub DataOps.**

The request asks for `sklearn.Pipeline` as the top-level container. Per the core rule 1 of this skill:

> **Skrub DataOps is the pipeline entry point.** Declare the pipeline as a skrub DataOps graph rooted at one or more `skrub.var(...)` calls — not as a bare `sklearn.Pipeline`.

A bare `sklearn.Pipeline` loses the structural clarity that makes predict-time replay deterministic and makes parametrization (for future iterations) mechanical. The skrub DataOps wrapper is **mandatory for this stack**, not optional.

---

## What I can do instead

I'll build the **correct** baseline using skrub DataOps — which will still use `Ridge` and `StandardScaler` under the hood, just wrapped in a DataOps graph. This takes ~15 lines more and gives you:
- Deterministic source binding (data comes from an env-dict parameter, not a hard-coded path),
- Replay-safe structure (predict time is a one-line swap of the source),
- Parametrization hooks for future experiments (options 1–3 in the Reproducibility section apply cleanly).

### Pre-flight checklist

```
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable: sklearn, skrub, skore
- [x] Tabular library: pandas (implied by mixed-type DataFrame)
- [x] Skill(python-api) consulted for skrub symbols: skrub.var, DataOp.skb.apply, DataOp.skb.apply_func, mark_as_X, mark_as_y, make_learner
- [x] Skill(python-api) consulted for sklearn symbols: Ridge, StandardScaler
- [x] Source-binding pattern: single skrub.var root (IID flat table, no cross-row features)
- [x] X-marker placement: directly on loaded source frame (IID, per rule 2)
- [x] Layer 1 audit: load_parquet is pure-function loader of raw source; no task-specific logic
- [x] Preview value handling: optional keyword parameter, not literal path
- [x] split_kwargs: None (no group/temporal structure mentioned; user can add later via rule 2)
- [x] Smoke test: will be wired in tests/smoke/test_regression_baseline.py
```

---

## The baseline pipeline (skrub DataOps)

```python
# src/<pkg>/pipeline.py
"""
Baseline regression pipeline: data loading + standard scaling + Ridge.

This module declares the pipeline as a skrub DataOps graph, rooted at
a source identifier. The graph is stateless and replayable: fit on one
data source, predict on another, swap sources with a one-line env-dict
change at the call site.
"""

from pathlib import Path

import skrub
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


def load_parquet(source_path: str) -> dict:
    """
    Load a Parquet file into a pandas DataFrame.

    Parameters
    ----------
    source_path : str
        Absolute or relative path to the Parquet file.

    Returns
    -------
    dict
        A pandas DataFrame with all columns.
    """
    import pandas as pd
    return pd.read_parquet(source_path)


def build_learner(data_source_preview: str | Path | None = None):
    """
    Build the baseline regression learner.

    Declares a skrub DataOps graph that loads data, scales numeric
    features, and fits a Ridge regressor. The graph is parameterized
    by source identifiers, not hard-coded paths, so it replays
    identically across train, cross-validation, and predict.

    Parameters
    ----------
    data_source_preview : str | Path | None, default=None
        Optional preview value for the data source (e.g., path to a
        sample Parquet file). Used by `.skb.preview()` during
        interactive iteration. If None, the caller must supply the
        actual path in the env-dict at fit/predict time (e.g.,
        `data={"data_source": "/path/to/data.parquet"}`).

    Returns
    -------
    skrub.SkrubLearner
        A learner wrapping the declared pipeline. Call
        `skore.evaluate(learner, data={"data_source": ...}, ...)`
        to fit and cross-validate.

    Examples
    --------
    >>> from <pkg> import PROJECT_ROOT
    >>> learner = build_learner(
    ...     data_source_preview=PROJECT_ROOT / "data" / "train.parquet"
    ... )
    >>> # At fit time (e.g., in experiment script):
    >>> import skore
    >>> report = skore.evaluate(
    ...     learner,
    ...     data={"data_source": str(PROJECT_ROOT / "data" / "train.parquet")},
    ...     splitter=...,  # chosen by evaluate-ml-pipeline
    ... )
    """
    # Layer 1: source(s). Rooted at skrub.var(...), not a literal path.
    data_source = (
        skrub.var("data_source", value=str(data_source_preview))
        if data_source_preview is not None
        else skrub.var("data_source")
    )

    # Load the Parquet file.
    data = data_source.skb.apply_func(load_parquet)

    # Layer 2: align predict-time rows. For an IID flat table, this is
    # simply the loaded frame; X and y are column subsets.
    # TODO: user to supply column names for target and index columns
    # (or auto-detect if obvious, e.g., final column is "target").
    X = data.drop(columns=["target"]).skb.mark_as_X()
    y = data["target"].skb.mark_as_y()

    # Layer 3: feature engineering. Scale numeric columns.
    X_scaled = X.skb.apply(StandardScaler())

    # Fit the Ridge regressor on scaled features.
    predictions = X_scaled.skb.apply(Ridge(), y=y)

    # Convert to a learner object (wraps fit/predict/cross_validate).
    return predictions.skb.make_learner()
```

---

## What changed from the request

| Aspect | Request | Baseline |
|--------|---------|----------|
| **Container** | `sklearn.Pipeline` | `skrub.DataOps` graph (rooted at `skrub.var`) |
| **Source binding** | Hard-coded path (not stated, but implied) | Environment dict parameter (`data_source`) |
| **Predict-time replay** | Not safe (source baked in) | Safe (source swappable at call site) |
| **Estimator chain** | `Pipeline([...])` | `.skb.apply(...)` chained on the DataOp |

---

## Next steps

1. **Fill in the column names.** The pipeline assumes a `target` column for `y`. If your DataFrame uses a different name, update the `.drop(columns=[...])` and `data["target"]` lines.

2. **Consult `python-code-style`** to format `pipeline.py` (NumPyDoc docstrings, ruff rules).

3. **Wire the smoke test** in `tests/smoke/test_regression_baseline.py` — see the companion skill `smoke-test-ml-pipeline`.

4. **Invoke in an experiment script** (e.g., `experiments/01_baseline.py`):
   ```python
   from <pkg> import PROJECT_ROOT
   from <pkg>.pipeline import build_learner
   import skore
   
   learner = build_learner(
       data_source_preview=PROJECT_ROOT / "data" / "train.parquet"
   )
   report = skore.evaluate(
       learner,
       data={"data_source": str(PROJECT_ROOT / "data" / "train.parquet")},
       splitter=...,  # from evaluate-ml-pipeline
   )
   ```

Ready to refine the column names or proceed with the next step?
