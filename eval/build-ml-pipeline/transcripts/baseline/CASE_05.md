# CASE_05 — Stateful step misclassified as stateless (leakage)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- skrub installed at 0.9.0.
- An existing skrub DataOps graph with `mark_as_X` / `mark_as_y`
  in place.]

Add target encoding for the `category` column. Just write a
`def target_encode(df): ...` that computes the mean target per
category and replaces the column. Attach it with `.skb.apply_func`.
```

## Response

# Stop — Leakage Risk Detected

**Do not proceed with this implementation.** The request violates rule 5 (Leakage rule) and will silently leak the test set into training.

## What's wrong

Target encoding is **stateful**. The mean target per category must be computed on the **training** data alone and then applied unchanged to the test data. Calling a plain function over the whole dataset (or even just materializing it at fit time) computes those means from the combined train+test data — poisoning the encoding.

**The litmus test:** would the output change if I called this function on the training subset alone vs. the whole frame? **Yes** — the categories in the test set might have different target means than they did in training. Therefore it is stateful.

## What to do instead

1. **Use sklearn's `TargetEncoder`** (available in scikit-learn 1.3+).
   - Attach it with `.skb.apply(TargetEncoder(), y=y)` after `mark_as_y`.
   - The `y=y` argument tells skrub to pass the target to the estimator's `fit`.

2. **If you need custom logic**, author a sklearn-compatible estimator:
   ```python
   from sklearn.base import BaseEstimator, TransformerMixin

   class CustomTargetEncoder(BaseEstimator, TransformerMixin):
       def fit(self, X, y=None):
           # Learn: compute means from y only
           self.encoding_ = X.groupby(...)[...].mean()  # fit on training y
           return self

       def transform(self, X):
           # Apply: replace column with learned encoding
           return X.map(self.encoding_)
   ```
   Then attach:
   ```python
   X_encoded = X.skb.apply(CustomTargetEncoder(), y=y)
   ```

## Next step

**Invoke `python-api`** to confirm the `TargetEncoder` import path and signature (does it exist in the installed sklearn version? What are the exact parameters?), then rewrite the pipeline step using the estimator + `.skb.apply(...)` pattern.

Once you have the correct import and signature, return here and we'll integrate it into the pipeline.
