# Evaluation: Target Encoding with build-ml-pipeline Skill

## Assessment

**The requested implementation contradicts the skill's core leakage rule (Rule 5).**

The request asks for a stateless function `def target_encode(df): ...` attached via `.skb.apply_func`. However, target encoding **is inherently stateful** and must NOT be implemented as a plain function.

### Why This Matters

From SKILL.md — Rule 5 (Leakage rule):
- "Any computation using statistics learned from the data (means, medians, quantiles, vocabularies, target distribution) MUST be stateful."
- Target encoding is explicitly listed as a classic leakage trap: "target encoding (must `fit` on training y only)"
- Litmus test: "would this output change if I called it on the training subset alone vs the whole frame? If yes → stateful"

### The Problem with Plain `.skb.apply_func`

A plain function computing mean target per category from the full dataset will:
1. **Learn from test data** — computing category means on the entire dataset (train + test combined) leaks test statistics into the fit phase
2. **Silently break cross-validation** — prior sklearn estimates are learned on test folds, producing optimistic metrics
3. **Fail at predict time** — categories in new data that weren't seen at fit time cannot map to a learned mean

### Correct Approach

Target encoding **must** be implemented as a stateful sklearn transformer:

```python
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class TargetEncoder(BaseEstimator, TransformerMixin):
    """Stateful target encoder learning mean target per category."""
    
    def fit(self, X, y):
        # Learn category means from training y only
        self.mapping_ = X.groupby(X.columns[0])[y].mean().to_dict()
        return self
    
    def transform(self, X):
        # Apply learned mapping; unknown categories map to global mean
        return X.iloc[:, 0].map(self.mapping_).fillna(y.mean()).values
```

Attach via **`.skb.apply(...)`** (not `.apply_func`), which ensures:
- Statistics are learned *only* on the training set during fit
- The learned mapping is reapplied unchanged at predict time
- Cross-validation and holdout evaluation see no leakage

## Verdict

**Skill applies correctly; implementation request violates Rule 5.** The skill would reject the plain-function approach and direct the user to use a stateful estimator instead. This is the skill protecting the experiment from a silent but critical bug.

## Recommendation

Use `.skb.apply(TargetEncoder())` in the pipeline, not `.skb.apply_func` with a plain function.
