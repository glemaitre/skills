# Setting Up a Baseline ML Pipeline

I'll create a simple baseline pipeline with `StandardScaler` and `Ridge` regression as requested.

## src/<pkg>/pipeline.py

Here's the implementation:

```python
"""Baseline regression pipeline using sklearn.Pipeline."""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge


def build_pipeline():
    """
    Build a baseline regression pipeline.
    
    Returns a sklearn Pipeline with:
    - StandardScaler for feature scaling
    - Ridge regressor for predictions
    
    Returns
    -------
    sklearn.pipeline.Pipeline
        Fitted pipeline ready for use.
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("ridge", Ridge()),
    ])
    return pipeline
```

## Implementation Notes

- **StandardScaler**: Normalizes numeric features by removing the mean and scaling to unit variance
- **Ridge**: Linear regression with L2 regularization to prevent overfitting
- **Pipeline**: Chains the preprocessing and model steps together, ensuring consistent transformations at both fit and predict time

The pipeline can be used like any sklearn estimator:

```python
from src.<pkg>.pipeline import build_pipeline

# Create pipeline
pipe = build_pipeline()

# Fit on training data
pipe.fit(X_train, y_train)

# Make predictions
predictions = pipe.predict(X_test)
```

## Next Steps

1. Load your tabular data (mixed-type DataFrame)
2. Pass numeric features through the pipeline
3. For mixed-type data, you may want to preprocess categorical features separately or use a preprocessor like `ColumnTransformer` to handle different feature types
4. Integrate with `skore.evaluate()` for cross-validation and scoring

This provides a solid baseline for your regression task.
