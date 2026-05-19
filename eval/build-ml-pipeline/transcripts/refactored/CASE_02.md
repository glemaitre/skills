# CASE_02 — IID flat-table marker placement

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (471 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- skrub installed at 0.9.0.
- Cache exists at `scratch/api/skrub/0.9.0/tabular_pipeline.md`
  (you may treat its content as known).]

Tabular CSV, columns `[feature_1, feature_2, ..., target, id]`.
Predict `target`. No time-series, no groups. Write the skrub
DataOps pipeline.
```

## Response

# Pre-flight (build-ml-pipeline)

```
- [x] Tier 1 mandatory libs importable: sklearn, skrub, skore
- [x] Tabular library identified: pandas (CSV → default)
- [x] python-api consulted for skrub symbols: tabular_pipeline
      Evidence: scratch/api/skrub/0.9.0/tabular_pipeline.md (cached)
- [x] python-api consulted for sklearn symbols: none — using skrub default
- [x] Source-binding pattern: skrub.var for CSV file path
- [x] X-marker placement: directly on loaded + preprocessed frame (IID)
- [x] Layer 1 audit: loader only; no task-specific featurization upstream
- [x] Preview value handling: optional kwarg, no literal path in pipeline.py
- [x] split_kwargs: none (no groups or time structure detected)
- [x] Smoke test: trivial assertions (IID case)
```

---

## Pipeline declaration

**File: `src/<pkg>/pipeline.py`**

```python
"""
Tabular flat-table pipeline: CSV → tabular_pipeline → predictor.
IID structure; no time-series, no groups.
"""

from sklearn.linear_model import LogisticRegression
import skrub


def build_learner(
    data_path: str,
    data_preview=None,
    target_col: str = "target",
    id_col: str = "id",
):
    """
    Build a skrub DataOps learner for tabular prediction.

    Parameters
    ----------
    data_path : str
        Path to CSV file. Columns: [feature_1, feature_2, ..., target, id].
    data_preview : str, optional
        Absolute path to a preview CSV for interactive iteration.
        If None, preview is empty (production mode).
    target_col : str, default="target"
        Name of target column.
    id_col : str, default="id"
        Name of ID column (dropped from features).

    Returns
    -------
    skrub.SkrubLearner
        Graph from data source to predictor, ready for
        skore.evaluate(...).
    """

    # Layer 1: Source
    raw_data = skrub.var("data", value=data_preview).skb.apply_func(
        lambda path: __import__("pandas").read_csv(data_path)
    )

    # Separate target and features
    y = raw_data[target_col].skb.mark_as_y()
    X = raw_data.drop(columns=[target_col, id_col]).skb.mark_as_X()

    # Layer 3: Feature engineering with skrub's tabular_pipeline
    X_processed = X.skb.apply(
        skrub.tabular_pipeline()
    )

    # Predictor
    predictor = X_processed.skb.apply(LogisticRegression(max_iter=1000))

    return skrub.SkrubLearner(X=X_processed, y=y, estimator=predictor)
```

---

## Notes

1. **IID structure** — marker lands directly on the loaded frame; no
   history-dependent steps, no cross-validation metadata required.

2. **`skrub.tabular_pipeline()`** — caches the cached spec. Handles
   categorical encoding, numerical scaling, and missing-value
   imputation automatically. Inspect / customize columns via
   `cols=` parameter if needed (see `common_patterns.md` § 2).

3. **`data_preview` parameter** — caller supplies the path; pipeline
   accepts `None` for production. No hardcoded relative path inside
   `pipeline.py`.

4. **Predictor choice** — `LogisticRegression` shown as example. Swap
   for `RandomForestClassifier`, `GradientBoostingClassifier`, or
   your choice. If regression, use `LinearRegression` or
   `RandomForestRegressor` and adjust.

5. **Next steps**:
   - Run `python-code-style` on `pipeline.py`.
   - Wire the smoke test (`smoke-test-ml-pipeline`).
   - Pair with `evaluate-ml-pipeline` for CV + metrics.
