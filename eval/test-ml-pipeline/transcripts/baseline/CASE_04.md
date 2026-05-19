# CASE_04 — Dispatch table: future categories not implemented

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/test-ml-pipeline/SKILL.md` (217 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/03_target_transform.md` exists, approved, done with metrics.
- `tests/smoke/` exists with prior smoke tests.]

The metrics drifted between 02 and 03. Can we lock that in with a
regression test?
```

## Response

```
Pre-flight (test-ml-pipeline):
- [x] `journal/03_target_transform.md` exists and is at least `approved`
- [x] `experiments/03_target_transform.py` exists with the matching stem
- [x] Test category picked: regression
- [ ] Subskill dispatched: `regression-test-ml-pipeline`
- [ ] Test file stem decided: `tests/regression/test_03_target_transform.py`
- [x] pytest is on the project's dependency manifest
```

---

## Hand-off to `regression-test-ml-pipeline`

You've identified the right problem: metrics drifted between `02`
and `03`, and you want to capture that contract so future edits
don't regress silently.

**However:** `regression-test-ml-pipeline` is **not yet implemented**
in v1. The dispatch table reserves it, but the subskill doesn't
exist yet.

### What you need to do now

1. **Document the regression contract manually** in a comment near
   the top of `experiments/03_target_transform.py` (or in the design
   note's metrics section). Record:
   - The metrics from `02` (baseline).
   - The metrics from `03` (current).
   - The acceptable drift range (e.g., "F1 must stay ≥ 0.78").

2. **Add a smoke test for `03`** if one doesn't already exist.
   Route to `smoke-test-ml-pipeline` to draft
   `tests/smoke/test_03_target_transform.py`. The smoke test won't
   *compare* to `02`, but it will *run* `03` and catch structural
   breaks.

3. **Plan the regression-test feature** for a future workspace
   iteration. When you're ready to implement it, `regression-test-ml-pipeline`
   will own:
   - Loading metrics from prior experiment checkpoints.
   - Asserting the current run stays within acceptable drift.
   - CI integration to fail the build if drift exceeds thresholds.

**For now:** the contract lives in prose + the smoke test covers
structural safety. Ready to draft the smoke test for `03`?
