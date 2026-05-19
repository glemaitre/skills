# skore.evaluate() Signature

For skore version 0.18.0, the signature of `skore.evaluate()` is:

```python
skore.evaluate(
    estimator,
    X,
    y,
    *,
    splitter=0.2,
    pos_label=None,
    n_jobs=None
)
```

## Parameters

- **estimator**: A scikit-learn compatible estimator or list of estimators for comparison
- **X**: Feature matrix (array-like or list of array-like when comparing multiple estimators)
- **y**: Target vector
- **splitter**: Controls data splitting strategy (default: 0.2 for 80/20 split)
  - Float: train-test split ratio
  - "prefit": assumes pre-fitted estimator
  - Int: number of cross-validation folds
  - Cross-validation object (e.g., KFold)
- **pos_label**: Positive class label for binary classification metrics
- **n_jobs**: Number of parallel jobs for execution

## Returns

An evaluation report object: `EstimatorReport`, `CrossValidationReport`, or `ComparisonReport` depending on the evaluation strategy used.

## Notes

- Parameters after the `*` (splitter, pos_label, n_jobs) are keyword-only arguments
- The function serves as a top-level dispatcher that creates the appropriate report class based on the evaluation strategy
