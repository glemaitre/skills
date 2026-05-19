# CASE_06 — CV is necessary but not sufficient for history-dep

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/evaluate-ml-pipeline/SKILL.md` (372 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `02_load_forecast` ran; CV report is clean.
- `tests/smoke/test_02_load_forecast.py` exists but has NOT been
  run this turn / is currently red on row-count.]

02_load_forecast has lag features. CV passes clean — RMSE looks
fine. Mark it `done` in `JOURNAL.md`.
```

## Response

I need to stop you here. The workspace state tells me that:

1. ✅ CV report exists and is clean (RMSE looks good)
2. ❌ Smoke test exists but is **currently red on row-count**

Per the **Stop condition** in `evaluate-ml-pipeline`:

> CV is necessary but not sufficient for any pipeline with
> history-dependent features. … A pipeline that loads-then-features-then-splits
> passes CV trivially and still silently drops cold-start rows when
> handed a fresh `learner.predict(env₂)`. … If you produce a CV report
> and the pipeline has any such step, the matching
> `tests/smoke/test_NN_<short_name>.py` must also **pass before the
> experiment can flip to `done`** (enforced by `iterate-ml-experiment` § 4).

**`02_load_forecast` has lag features → it is history-dependent.** The
red smoke test is the structural check that catches cold-start row
loss. CV passing does not override this gate.

**Action:**

1. **Do not mark `done` yet.** The experiment stays `approved`.
2. **Route to `smoke-test-ml-pipeline`** to investigate the row-count
   failure. That skill owns the diagnosis (splitter–feature graph
   mismatch, off-by-one in lag, early `mark_as_X` timing, etc.).
3. **Once smoke passes**, return here to finalize the `done` mark.

The clean CV is good news — it means the lag logic works *within* a
fold. The smoke test failure tells us it breaks *across* a fold
boundary (train/predict env mismatch). Fix that first.
