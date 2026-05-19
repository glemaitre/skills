# Target Encoding: Why `apply_func` Won't Work Here

I cannot recommend using `.skb.apply_func` for target encoding. Here's why:

## The Problem: Leakage & Statefulness

Target encoding is a **stateful** transformation that **learns from training data**. It computes the mean target value for each category, and those computed means must be:

1. **Learned during training only** — from the training set's category-to-target mapping
2. **Applied identically during prediction** — using the same learned mapping

When you write `def target_encode(df):` and attach it via `.skb.apply_func`, you're marking it as **stateless**. This means:

- The function will see the entire DataFrame (train + validation + test merged)
- It will compute statistics from *all* data, causing **data leakage**
- Validation and test metrics will be artificially inflated

This violates the **leakage rule** and **statelessness rule** in the skrub DataOps pattern.

---

## The Solution: Use a Stateful Estimator

Instead, use sklearn's built-in **TargetEncoder** (or implement a custom `BaseEstimator` + `TransformerMixin`). Attach it via `.skb.apply` (not `.apply_func`):

```python
from sklearn.preprocessing import TargetEncoder

predictions = (
    skrub.var("<source>", preview)
    .skb.apply_func(load_data)
    .skb.mark_as_X()
    .skb.mark_as_y()
    ...
    .skb.apply(TargetEncoder(), on=["category"])
)
```

The key difference:
- `.skb.apply` wraps the estimator in a learner step
- During training, TargetEncoder **fits** on training data
- During prediction, it **transforms** using learned means
- Validation/test stay isolated from training statistics

---

## Confirm the API

Consult the `python-api` skill to verify the exact signature and availability of `sklearn.preprocessing.TargetEncoder` for your sklearn version. The pattern ensures reproducibility, prevents leakage, and plays well with skrub's learner split (train/predict isolation).
