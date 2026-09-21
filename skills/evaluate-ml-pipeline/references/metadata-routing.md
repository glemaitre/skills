# Metadata routing: Pattern A vs Pattern B

`skore.evaluate` accepts `estimator`, `X`/`y` **or** `data`, and
`splitter`. It does **not** take `groups=` or other `split()`
kwargs. Those kwargs, when needed, live on the DataOp X marker.

`G-CV-SPLITTER` still chooses the sklearn splitter (mapping table
in `evaluate-ml-pipeline` rule 3). These patterns only say **where
that object is passed**. Confirm signatures with
`python -m skore_skills api get`.

This document routes cross-validation metadata only. Custom metric
kwargs such as `sample_weight` follow
`references/custom-metrics.md`; never put them in `split_kwargs`.

skrub `mark_as_X`:
https://skrub-data.org/stable/reference/generated/skrub.DataOp.skb.mark_as_X.html

## Does `split(X, y)` need extra kwargs?

| Splitter | Extra `split()` kwargs | Pattern |
|---|---|---|
| `KFold` | none | **A** |
| `RepeatedKFold` | none | **A** |
| `ShuffleSplit` | none | **A** |
| `TimeSeriesSplit` | none (rows must already be time-ordered) | **A** |
| `GroupKFold` | `groups` | **B** |
| `GroupShuffleSplit` | `groups` | **B** |
| `StratifiedKFold` *(avoid)* | none | **A** if forced |
| `StratifiedGroupKFold` *(avoid)* | `groups` | **B** if forced |
| `LeaveOneGroupOut` *(avoid)* | `groups` | **B** if forced |
| Custom splitter | whatever its `split` declares | **A** if none; **B** otherwise |

## Pattern A — pass `splitter=` to `evaluate`

Use when the chosen splitter's `split(X, y)` needs nothing else
(`KFold`, `TimeSeriesSplit`, `RepeatedKFold`, …).

```python
report = skore.evaluate(
    build_learner(),
    data={"data_dir": str(DATA_DIR)},
    splitter=KFold(n_splits=5),
)
```

The X marker has **empty** `split_kwargs` and **no** `cv=`. An
omitted `splitter=` here is an 80/20 holdout, not the gated CV.

## Pattern B — `cv=` + `split_kwargs` on the DataOp; omit `splitter=`

Use when `split(X, y, **kwargs)` needs keys `evaluate` cannot take
(typically `groups`). skrub requires `cv=` whenever `split_kwargs`
is set; `cv=<int>` is not a splitter (skore cannot call `.split` on
it).

**Build** (`pipeline.py`) — placeholder `cv` is the mapping-table
splitter, not a second `G-CV-SPLITTER` gate:

```python
from sklearn.model_selection import GroupKFold

X = data.drop(columns=[..., "customer_id"]).skb.mark_as_X(
    cv=GroupKFold(),
    split_kwargs={"groups": data["customer_id"]},
)
```

**Evaluate** — do **not** pass `splitter=`. skore reuses the DataOp
`cv` **and** `split_kwargs`. An explicit `splitter=` **overrides
`cv` and drops `split_kwargs`**, so `GroupKFold` then raises
`groups` is None.

```python
report = skore.evaluate(
    build_learner(),
    data={"data_dir": str(DATA_DIR)},
)
```

## Traps

- `mark_as_X(split_kwargs=...)` without `cv=` — skrub raises at
  construction.
- `mark_as_X(cv=5, split_kwargs={"groups": ...})` — not Pattern B.
- `evaluate(..., splitter=GroupKFold())` when groups are only on
  the DataOp — `groups` is None.

## Empty `split_kwargs`

If the X marker has no metadata and you can confirm there is no
group or time structure, Pattern A with `KFold`. Possible
**groups** with empty `split_kwargs` → return to
`build-ml-pipeline`. **Time** with empty `split_kwargs` is
expected; fire the time-ordered AskUserQuestion (Pattern A if
the user picks `TimeSeriesSplit`). Do not invent a `times=` key.
