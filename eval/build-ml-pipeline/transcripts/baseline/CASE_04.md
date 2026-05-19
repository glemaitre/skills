# CASE_04 — `skrub.X / skrub.y` as roots — refuse

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (805 lines)

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

# Pre-flight (build-ml-pipeline)

**STOP — Stop condition violated before continuing.**

Your draft uses `skrub.X(...)` and `skrub.y(...)` as roots, which is **forbidden** by rule 2 and the "Symbol from memory" Stop condition. I must consult `python-api` for the correct skrub entry point first.

Let me fetch the skrub 0.9.0 API surface:

<Skill(python-api)>
Query: skrub 0.9.0 — top-level entry points for declaring a DataOps graph; confirm whether `skrub.X` and `skrub.y` exist and whether they are acceptable roots for a pipeline declaration.
</Skill(python-api)>

---

## Why your draft is blocked

The Stop condition says:

> **`skrub.X(...)` / `skrub.y(...)` are not acceptable as graph roots.** They are sugar for `var("X", value).skb.mark_as_X()` and `var("y", value).skb.mark_as_y()`, which (1) bake the marker at the source — defeating Layer 1 of rule 2; (2) force a pre-loaded, pre-split binding so the graph cannot be replayed at predict time against a fresh source identifier; (3) collapse the three-layer pattern even when the data has cross-row features (lags, joins, rolling windows), silently re-enabling the late-`mark_as_X` bug.

And rule 2 states:

> When tempted (typically because materialising `(X, y)` upstream "feels simpler"), return to rule 2 and root the graph on `skrub.var("<source>", preview)` — at least one source identifier per raw input, plus a `predict_grid` identifier when the data is panel / time-series.

---

## What I need from you before I can continue

I have three quick questions:

1. **Is your data IID flat-table?** That is:
   - One row = one training example (no time ordering, no repeated measures, no groups)?
   - No future-looking features (no lag, no rolling window, no target shift)?
   
   If yes → we root on `skrub.var(...)` and land the marker directly on your source frame (still very simple).  
   If no → we need to know the structure (time-series? panel / group? cold-start?) so the marker lands in the right layer.

2. **Where is `data` coming from in your actual experiment?** Is it:
   - A file path passed at runtime (e.g. `data_dir` parameter)?
   - A pre-materialized DataFrame that you're testing with locally?  
   
   The answer determines whether the root is `skrub.var("data")` (file path) or `skrub.var("data", value=data)` (testing).

3. **For the encoder and predictor**: What type of data are we encoding / predicting on?
   - Classification or regression?
   - What are the column types in your dropped feature set (numeric, categorical, mixed)?
   - Any missing values?

Once you answer, I'll:
- Show you the correct root using `skrub.var(...)` (not the shortcuts).
- Wire the encoder (via a skrub selector pattern or tabular defaults).
- Attach the predictor.
- Emit the full Pre-flight checklist with all stops clear.
