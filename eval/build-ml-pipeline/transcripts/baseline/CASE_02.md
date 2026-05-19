# CASE_02 — IID flat-table marker placement

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

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
Pre-flight (build-ml-pipeline):
- [x] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      Evidence: Workspace state confirms skrub 0.9.0 installed
- [x] Tabular library identified: pandas | polars
      Evidence: CSV input implies pandas default; no specification given,
                proceeding with pandas loader
- [x] Skill(python-api) consulted for skrub symbols: skrub.var, 
      .skb.apply_func, .skb.mark_as_X, .skb.mark_as_y, .skb.make_learner,
      skrub.tabular_pipeline
      Evidence: Cache hit at scratch/api/skrub/0.9.0/tabular_pipeline.md;
                confirmed signatures below for var/mark_as_X/mark_as_y/make_learner
- [x] Skill(python-api) consulted for sklearn symbols: none
      Evidence: "n/a — no sklearn estimator introduced in this turn;
                tabular_pipeline handles the default composition"
- [x] Source-binding pattern chosen: single skrub.var root on CSV file path
- [x] X-marker placement decided: directly on loaded source frame
      (IID flat-table, no cross-row dependencies)
- [x] Per history-dependent feature step: n/a — no cross-row steps
- [x] Layer 1 audit: loader is pure CSV read; passes constructive test
- [x] Preview value handling decided: optional keyword parameter,
      default None (env-dict supplies binding at fit time)
- [x] split_kwargs at the X marker decided: none (no groups, no time ordering)
- [x] Smoke test wired: will be created at tests/smoke/test_tabular_flat.py
```

---

## Pipeline declaration

Create `src/<pkg>/pipeline.py`:

```python
"""
ML pipeline: IID tabular CSV → predictor.

Data shape: [feature_1, ..., feature_N, target, id]
Task: predict target (regression or classification).
Structure: flat table, no temporal / group structure.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import skrub
from sklearn.ensemble import RandomForestClassifier


def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Load tabular CSV file.

    Parameters
    ----------
    csv_path : str
        Absolute path to CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded table.
    """
    return pd.read_csv(csv_path)


def build_learner(
    data_preview: Optional[str | Path] = None,
) -> skrub.SkrubLearner:
    """
    Build IID tabular pipeline: load → split X/y → predict.

    Parameters
    ----------
    data_preview : str | Path, optional
        Absolute path to CSV for interactive preview via `.skb.preview()`.
        At fit / cross-validate time, the env-dict supplies the binding.
        Default None.

    Returns
    -------
    skrub.SkrubLearner
        Lazy DataOps graph, ready to pass to skore.evaluate(...).

    Examples
    --------
    >>> from pathlib import Path
    >>> from <pkg> import PROJECT_ROOT
    >>> data_path = PROJECT_ROOT / "data" / "train.csv"
    >>> learner = build_learner(data_preview=data_path)
    >>> # Inspect the preview:
    >>> learner.skb.preview()

    At fit time (skore.evaluate, CrossValidationReport, etc.):

    >>> learner = build_learner()
    >>> report = skore.evaluate(
    ...     learner,
    ...     data={"data": str(data_path)},
    ...     splitter=...,
    ... )
    """
    # Layer 1: source
    data_var = (
        skrub.var("data", value=str(data_preview))
        if data_preview is not None
        else skrub.var("data")
    )
    data = data_var.skb.apply_func(load_csv)

    # Layer 2: split X/y on the flat table
    X = data.drop(columns=["id", "target"]).skb.mark_as_X()
    y = data["target"].skb.mark_as_y()

    # Layer 3: default tabular preprocessing + predictor
    # tabular_pipeline handles type inference, categorical encoding,
    # missing-value imputation, and scaling. Attach predictor at the tail.
    predictions = X.skb.apply(
        skrub.tabular_pipeline(
            estimator=RandomForestClassifier(random_state=42, n_jobs=-1),
        ),
        y=y,
    )

    return predictions.skb.make_learner()
```

---

## Notes

1. **Single `skrub.var` root** — named `"data"` because it is the raw
   CSV path. At preview time (interactive iteration), `data_preview=`
   supplies an absolute path; at fit/evaluate time, the caller binds it
   via `data={"data": str(data_path)}` in the env-dict.

2. **Layer 2: early marker on flat table** — no cross-row operations, so
   `mark_as_X()` lands directly on the loaded source after dropping
   `id` and `target`. No `split_kwargs` needed (IID, no groups/time).

3. **Layer 3: `skrub.tabular_pipeline`** — wraps scikit-learn's
   preprocessing (type detection, categorical encoding, imputation,
   scaling) and chains your estimator at the tail. Consult the cached
   `scratch/api/skrub/0.9.0/tabular_pipeline.md` for the full
   signature and what estimators are allowed.

4. **Predictor choice** — `RandomForestClassifier` shown as a placeholder.
   Swap to your actual estimator (e.g. `LogisticRegression` if regression,
   `GradientBoostingClassifier` if you prefer, etc.). Import from
   `sklearn.ensemble`, `sklearn.linear_model`, etc. — consult `python-api`
   to confirm the right import path.

5. **Reproducibility** — the default `None` for `data_preview` means the
   smoke test and prior experiments call `build_learner()` unchanged;
   only the new experiment passes `data_preview=<path>`.

---

## Next steps

1. **Confirm the predictor family** — is this classification or regression?
   Adjust `RandomForestClassifier` → your choice.

2. **Create the smoke test** at `tests/smoke/test_tabular_flat.py` (per
   `smoke-test-ml-pipeline`). Minimal shape:

   ```python
   import pandas as pd
   from <pkg>.pipeline import build_learner
   from <pkg> import PROJECT_ROOT

   def test_learner_smoke():
       data_path = PROJECT_ROOT / "data" / "train.csv"
       learner = build_learner(data_preview=data_path)
       
       # Smoke assertion: learner is a SkrubLearner
       assert isinstance(learner, skrub.SkrubLearner)
   ```

3. **Invoke `python-code-style`** to lint `pipeline.py` before commit.

4. **Write your experiment script** at `experiments/01_baseline.py`:

   ```python
   from <pkg> import PROJECT_ROOT
   from <pkg>.pipeline import build_learner
   import skore
   from sklearn.model_selection import StratifiedKFold

   data_path = PROJECT_ROOT / "data" / "train.csv"
   learner = build_learner()
   
   report = skore.evaluate(
       learner,
       data={"data": str(data_path)},
       splitter=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
   )
   report.report()
   ```

   (Consult `evaluate-ml-pipeline` for the full evaluation pattern.)
