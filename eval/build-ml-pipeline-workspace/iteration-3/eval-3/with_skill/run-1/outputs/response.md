# Evaluation Response: build-ml-pipeline (iteration 2)

## Request Summary
Add target encoding for the `category` column using a `def target_encode(df): ...` function with `.skb.apply_func`.

## Skill Assessment

**VIOLATION DETECTED: Rule 5 — Leakage rule**

The request asks to implement target encoding as a custom stateless function attached via `.skb.apply_func`. This is **forbidden** by Rule 5 and explicitly called out in the built-ins mapping table at lines 394–395 of SKILL.md:

```
| Target encoding (categorical → mean of y per category) | **`sklearn.preprocessing.TargetEncoder`** (sklearn ≥ 1.3) | the built-in doesn't fit your target type or smoothing strategy |
```

### Why This Fails

**Definition of stateful (Rule 4, lines 362–375):**
> Stateful — needs statistics / vocabulary / learned parameters fit on the **training** data and re-applied unchanged to the **test** data. Examples: ... target encoding ...

Target encoding computes a **mean of `y` per category value**. This is learned from the training set only. If you call such a function as `.skb.apply_func` over the whole frame:

1. The function runs on `X_train + X_test` merged together
2. The category means are computed from **both** train and test rows
3. Those statistics are then "applied" during prediction
4. Result: **test-set statistics bleed into the learned encoding** — classic leakage

**Litmus test (Rule 5, lines 419–421):**
> would this output change if I called it on the training subset alone vs the whole frame? If yes → stateful → `.skb.apply` with an estimator, never `.skb.apply_func`.

For target encoding: **Yes, the output changes.** If you compute category means on `X_train` alone vs on `X_train + X_test`, you get different values. Therefore it is stateful.

### Correct Approach

Use the built-in `sklearn.preprocessing.TargetEncoder` (sklearn ≥ 1.3) via `.skb.apply`:

```python
from sklearn.preprocessing import TargetEncoder

# Instead of:
# X = X.skb.apply_func(target_encode)  # LEAKS

# Do:
X = X.skb.apply(TargetEncoder(), cols=["category"])
```

The `TargetEncoder`:
- **Fits** on training data, learning the mean `y` per category
- **Transforms** identically on test data without re-learning
- Handles unknown categories at prediction time safely
- Is built-in and tested in sklearn (no custom subclass needed)

### Why This Rule Exists

Rule 5 and its mapping table exist to prevent silent leakage. The evaluation framework (smoke-test-ml-pipeline) catches **structural** problems like late `mark_as_X`, but not statistical ones like custom leaky encoders. The built-ins list is a shortcut: *"If you are about to hand-roll this operation, stop and use this sklearn/skrub class instead."*

## Outcome

**The request cannot be fulfilled as stated.** The skill explicitly forbids implementing target encoding as a custom stateless function. To proceed, either:

1. **Use the built-in:** Switch to `sklearn.preprocessing.TargetEncoder` via `.skb.apply`
2. **Justify a custom path:** If the built-in's smoothing strategy or target type doesn't fit your needs, author a `BaseEstimator` + `TransformerMixin` subclass and attach via `.skb.apply` (not `.skb.apply_func`)

---

**Evidence:** SKILL.md lines 380–421 (Rule 5 — Leakage rule), lines 393–417 (built-ins mapping table and authoring order)
