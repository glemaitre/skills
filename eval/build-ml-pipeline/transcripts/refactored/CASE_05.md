# CASE_05 — Stateful step misclassified as stateless (leakage)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (471 lines)

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

**STOP — rule violation detected.**

Target encoding **learns statistics from the training data** (the mean target per category) and must apply those learned statistics unchanged to the test data. This is **stateful**, not stateless.

Calling a plain function via `.skb.apply_func` over the whole frame leaks test into training:

- At fit time: the function sees the full training set → computes means from training labels → encodes training data. ✓
- At predict time: the function runs again on the predict set with no learned state → recomputes means from the predict set (which has no labels) or falls back to the training means baked into the function. ✗ Either way, the encoding changes between fit and predict, or the function breaks when `y` is unavailable.

**Solution:** Use a stateful `BaseEstimator` + `.skb.apply`.

Before I write code, I need to confirm:

1. **Does the predict-time grid have target values?** Or are you encoding at predict time with no labels available?
   - If no labels at predict → must learn and freeze the encoding at fit only.
   - If labels exist at predict → still must fit only on training to avoid test leakage in cross-validation.

2. **Which library is your frame** — pandas or polars?

3. **Should I look up the sklearn `TargetEncoder` signature** to see if there's a built-in, or do you want a custom implementation?

Once you answer (1), I'll:
- Consult `python-api` for the right base classes / built-in encoder.
- Write a stateful transformer.
- Attach it correctly with `.skb.apply`.
- Confirm the rule 4 / rule 5 decision in a comment.
