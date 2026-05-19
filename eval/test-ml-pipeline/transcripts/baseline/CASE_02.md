# CASE_02 — No design note → refuse + hand off

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/test-ml-pipeline/SKILL.md` (217 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `experiments/03_target_transform.py` exists (someone wrote it directly).
- `journal/03_target_transform.md` does **not** exist.
- `tests/smoke/` exists.]

Write the smoke test for `experiments/03_target_transform.py`.
```

## Response

```
Pre-flight (test-ml-pipeline):
- [ ] `journal/03_target_transform.md` exists and is at least `approved`
      ✗ MISSING — abort test creation
- [ ] `experiments/03_target_transform.py` exists with the matching stem
      ✓ exists
- [ ] Test category picked: smoke | regression | distribution | …
      ✗ blocked by missing design note
- [ ] Subskill dispatched: `smoke-test-ml-pipeline` | …
      ✗ blocked by missing design note
- [ ] Test file stem decided: `tests/smoke/test_03_target_transform.py`
      ✗ blocked by missing design note
- [ ] pytest is on the project's dependency manifest (per
      `data-science-python-stack` § Tier 1)
      ✗ not checked yet
```

## Stop

I cannot write the smoke test yet. **The pairing rule is hard:** a test file only exists if the design note exists first. The design note is the contract; the test asserts the contract holds.

Right now:
- ✓ `experiments/03_target_transform.py` exists
- ✗ `journal/03_target_transform.md` does **not** exist

### Next step

Hand off to **`iterate-ml-experiment`** to author and approve the design note for `03_target_transform` first. Once `journal/03_target_transform.md` is at least `approved`, come back here and I'll place `tests/smoke/test_03_target_transform.py` and dispatch to `smoke-test-ml-pipeline` to draft the assertions.

The design note answers: *What transform are we testing? What are the input/output contracts? What assumptions does the pipeline make about the target?* Those answers become the smoke test's assertions.
