# CASE_07 — `skore.evaluate` / `project.put` only in experiment script

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/evaluate-ml-pipeline/SKILL.md` (372 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `experiments/02_text_encoder.py` already produced a report.
- The user wants a "refreshed" version.]

Add a scratch probe that re-runs `skore.evaluate(learner, ...)` to
see the updated metrics, then `project.put("02_text_encoder",
report)` to refresh the cache.
```

## Response

I need to stop you here. The request violates a critical Stop condition in this skill.

---

## Stop: `skore.evaluate(...)` and `project.put(...)` belong only in `experiments/NN_*.py`

From the Stop conditions block:

> **`skore.evaluate(...)` and `project.put(...)` live only in
> `experiments/NN_*.py`.** The experiment script is the sole
> producer of a report in the workspace's skore Project.
> Re-running `evaluate` from a `scratch/` probe (or a notebook,
> or a one-off Python file in `src/`) duplicates the report
> under the same `key` and pollutes `project.summarize()` —
> the cross-experiment metrics view that `overview/summary.md`
> reads from.

**What happens if I write a scratch probe with `evaluate` + `project.put`:**

The probe will execute `project.put("02_text_encoder", report)`, which overwrites (or duplicates, depending on skore's ID-handling) the entry in the Project store. When `overview/summary.md` calls `project.summarize()` to enumerate all experiments, it sees either:
- A polluted Project with multiple artifacts under the same key, or
- A freshly updated artifact with no provenance (no audit trail showing *when* or *why* it was refreshed).

Both states break the contract that **the experiment script is the sole producer**.

---

## The correct path: re-run the experiment script

To refresh the report for `02_text_encoder`:

1. **Open `experiments/02_text_encoder.py`** (the existing file).
2. **Make any required changes** to the learner, data, or splitter.
3. **Run the script via `pixi run python experiments/02_text_encoder.py`**.

This re-execution:
- Calls `skore.evaluate(...)` in the canonical location.
- Calls `project.put("02_text_encoder", report)` in the canonical location.
- Produces a refreshed report with a clean audit trail.

If the script needs to be modified first (e.g., different splitter, added metrics), invoke the relevant skill (`build-ml-pipeline`, `evaluate-ml-pipeline`, or `iterate-ml-experiment`) to guide the edit. If the script is correct as-is and you just want to re-run it, do so directly:

```bash
pixi run python experiments/02_text_encoder.py
```

---

**What *would* a scratch probe be used for?** Reading the report after it's produced — e.g., extracting per-fold values, inspecting metric names, walking the report structure. That's a read-only operation against the already-stored artifact, not a re-producer. See `organize-ml-workspace` § "Scratch is read-only against the skore Project" for that pattern.
