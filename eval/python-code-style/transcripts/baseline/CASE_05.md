# CASE_05 — Numpydoc docstring convention

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-code-style/SKILL.md` (218 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- File is `src/claim_predictor/predictor.py`.
- `ruff.toml` exists with `pydocstyle.convention = "numpy"`.]

I just wrote `def predict_price(X, model): ...` — what should the
docstring look like? Just a one-line summary is fine.
```

## Response

For a public function in the stack, here's the numpydoc skeleton:

```python
def predict_price(X, model):
    """Predict option prices from a feature matrix.

    Parameters
    ----------
    X : pandas.DataFrame
        Feature matrix with one row per option.
    model : sklearn.base.BaseEstimator
        Fitted estimator with a ``predict`` method.

    Returns
    -------
    numpy.ndarray of shape (n_samples,)
        Predicted prices, one per row of ``X``.
    """
```

Key points for your function:

- **First line**: imperative mood ("Predict..." not "Predicts..."), with a period (numpy convention requires it).
- **Blank line** after the summary.
- **Parameters section**: type on the left, one-liner description on the right. Include shapes for arrays.
- **Returns section**: type and shape, then a description.

If you just want the one-liner for now and will fill in Parameters/Returns later, that's fine — ruff will flag `D401` (imperative mood) and `D405` (missing sections) until you do, but you can add them incrementally. Just make sure the summary starts with a verb and ends with a period.

Ready to write the function? Once you do, I'll run ruff on the file.
