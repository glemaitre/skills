# CASE_03 — History-dependent late `mark_as_X` trap

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/build-ml-pipeline/SKILL.md` (471 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- skrub installed at 0.9.0.
- The user is in early baseline construction.]

Time-series load forecast. Each row = (timestamp, region, load).
I want a 24-hour-ahead forecast. Write the loader so it computes
`y = load.shift(-24)` then drops the rows with `NaN` in `y`, and
we'll do `mark_as_X` on the result.
```

## Response

# ⛔ Stop — late mark issue detected

You've described a **late-`mark_as_X` topology** (rule 2 violation). The symptoms are exact:

1. **`y` computation requires a cross-row operation** — `.shift(-24)` looks forward 24 rows.
2. **`mark_as_X` comes *after* that shift** — on the result with NaNs already dropped.
3. **At predict time, this breaks:** the predict grid will be cold-start rows with no history after them, so `.shift(-24)` produces all-NaN, and `drop_nulls` deletes the entire prediction set silently.

---

## The three-layer fix

Before I write code, I need **two clarifications from you**:

### Q1: Predict-time grid shape
When you call `.predict(...)` on the fitted learner, what rows do you want forecasts for?

- **Option A:** a new CSV with columns `[timestamp, region, load]` (some recent window — the raw input).
- **Option B:** a sparse description like a list of `(timestamp, region)` tuples (the *target times* you want forecasts for, without loading values).
- **Option C:** something else (e.g., a range of dates × a set of regions)?

### Q2: Train / predict split
Will the train and predict portions be:

- **Disjoint dates** (e.g., train on Jan–Feb, predict on Mar)?
- **Overlapping or rolling** (e.g., train on a trailing 90 days, predict on the next 24 hours, repeat)?

---

## Why the topology matters

**The correct three-layer shape for your case:**

- **Layer 1:** Raw history file(s) loaded as-is. No shift, no target derivation.
- **Layer 2:** Predict-time grid (e.g., `(timestamp, region)` pairs of the times you want forecasts for) + a **stateful estimator** that:
  - At `fit`: takes the full history + the training grid, derives `y = load.shift(-24)`, drops NaN rows, and stores the result.
  - At `predict`: takes the history + the predict grid, derives `y_pred = load.shift(-24)` for each predict row (using real history values), and drops NaN rows **only if evaluating downstream** (not baked into the learner itself).
  - Returns `{X, y}` at fit; `{X}` at predict (no y).
- **Layer 3:** Feature engineering on the X-branch downstream of `mark_as_X`.

Once you answer Q1 and Q2, I'll:

1. **Consult `python-api`** for the exact skrub / sklearn estimator names needed.
2. **Write the code** with the three layers wired correctly.
3. **Wire the smoke test** so predict on cold-start rows actually works.

**Until then, do not put `drop_nulls` in the loader.** That's the structural debt being blocked.
