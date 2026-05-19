# CASE_02 — Refuse to write before approved design note

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/smoke-test-ml-pipeline/SKILL.md` (423 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `experiments/03_target_transform.py` exists (written directly).
- `journal/03_target_transform.md` does NOT exist.]

Smoke-test `experiments/03_target_transform.py` — I haven't
written the design note yet but the script's ready.
```

## Response

# STOP — Cannot proceed

You must write and approve `journal/03_target_transform.md` **before** writing the smoke test.

The pairing rule from `test-ml-pipeline` is hard:

> `tests/smoke/test_NN_<short_name>.py` exists only when
> `journal/NN_<short_name>.md` is at least `approved` *and*
> `experiments/NN_<short_name>.py` exists with the matching stem.

**Current state:**
- ✅ `experiments/03_target_transform.py` exists
- ❌ `journal/03_target_transform.md` does not exist

**What to do:**

1. **Route to `iterate-ml-experiment`** to write and iterate the design note
   (`journal/03_target_transform.md`). The note must include:
   - **Question**: what are you testing with the target transform?
   - **Method**: how is the transform applied in the pipeline?
   - **Status** (when approved): hardcode the CV-mean metric into the smoke test's soft assertion

2. **Return here** once the design note is at least `approved`.

3. Then I can write the smoke test for `test_03_target_transform.py`.

The design note is not a burden on the smoke test — it's the load-bearing dependency. Without it, I don't know:
- What the experiment's env-dict shape is (source binding: directory, grid+history, materialized `(X, y)`?)
- What CV-mean baseline to hardcode into the soft assertion
- What the X-marker placement should be (to validate that the smoke test correctly diagnoses the failure mode)

**Go to `iterate-ml-experiment` first.**
