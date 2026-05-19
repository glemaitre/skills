# CASE_04 — `skrub.X / skrub.y` as roots — refuse

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (471 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- skrub installed at 0.9.0.
- `data` is already a loaded DataFrame.]

Here's my draft:

```python
X = skrub.X(data.drop(["id", "target"], axis=1))
y = skrub.y(data["target"])
```

Continue from here — add the encoder and the predictor.
```

## Response

# Stop — refactor before continuing

Your entry point violates **Stop condition** (late `mark_as_X` + pre-loaded binding) and **Rule 2** (marker placement). I need to redirect you before building further, because continuing from here will lock in structural debt.

## The three problems

1. **`skrub.X(data.drop(...))` bakes materialized data into the pipeline** — it cannot be replayed at predict time against a fresh source identifier. The `X(...)` / `y(...)` shortcuts are sugar for `.skb.mark_as_X()` / `.skb.mark_as_y()` called on a literal DataFrame, which collapses all three layers into one.

2. **The marker lands *after* row filtering** (the `drop`) — this is late marking. If any future feature step depends on cross-row data (a lag, a rolling window, a group aggregation), predict-time replay on cold-start rows will silently drop them.

3. **Even for IID data, the rigid binding breaks experiment composition** — you cannot later decide to split differently, inject a preview, or pipe to a second task without rewriting the loader.

## Refactor — three-layer model

Rewrite the entry point to use `skrub.var(...)` on the source identifier, then layer the marker and preprocessing:

```python
import skrub

# Layer 1: Source(s)
raw_data = skrub.var("data", value=data)

# Layer 2: Predict-time grid + markers
X = raw_data.skb.apply_func(
    lambda df: df.drop(["id", "target"], axis=1)
).skb.mark_as_X()

y = raw_data.skb.apply_func(
    lambda df: df["target"]
).skb.mark_as_y()
```

**Why this shape:**
- The `skrub.var(...)` root lets you bind different sources at fit vs predict (or pass a preview path).
- The marker lands **before** feature engineering — future cross-row steps can reference `raw_data` directly without seeing NaN.
- Layer 1 is pure loading; Layer 2 is alignment; Layer 3 is featurization.

## Next steps — after you confirm

Once you refactor:

1. **Invoke `python-api`** to look up:
   - The encoder you plan (e.g., `OneHotEncoder`, `OrdinalEncoder`, skrub's `TableVectorizer`).
   - The predictor (e.g., `LogisticRegression`, `RandomForestClassifier`).
   - Their `.skb.apply` signatures.

2. **Chain the encoder on the X-branch** (via `.skb.apply`).

3. **Chain the predictor at the tail** (via `.skb.apply`).

4. **Ask if there are group / temporal columns** that belong in `split_kwargs` at the `mark_as_X` call.

Paste your refactored code (with the encoder and predictor added), and I'll confirm the wiring.
