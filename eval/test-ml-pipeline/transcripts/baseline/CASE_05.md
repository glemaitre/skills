# CASE_05 — pytest is the runner (no `# %%` scripts)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/test-ml-pipeline/SKILL.md` (217 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_text_encoder.md` approved.
- `tests/smoke/` exists.]

Let's just write the smoke test as a jupytext `# %%` script under
`experiments/02_text_encoder_smoke.py` so I can step through it.
```

## Response

I need to stop here and be direct: **that won't work within this workspace's structure, and I need to explain why.**

Here's the Pre-flight checklist:

```
Pre-flight (test-ml-pipeline):
- [x] `journal/02_text_encoder.md` exists and is approved
- [ ] `experiments/02_text_encoder.py` exists with the matching stem
      ⚠️  BLOCKER: you're asking for `experiments/02_text_encoder_smoke.py`
      instead. That breaks the pairing rule.
- [ ] Test category picked: smoke
- [ ] Subskill dispatched: `smoke-test-ml-pipeline`
- [ ] Test file stem decided: `tests/smoke/test_02_text_encoder.py`
- [x] pytest is on the project's dependency manifest
```

## The pairing rule is hard

The stem must be **exactly** the same across all three:

```
journal/02_text_encoder.md          ← approved design note
experiments/02_text_encoder.py      ← the experiment script
tests/smoke/test_02_text_encoder.py ← the smoke test
```

No `_smoke` suffix on the experiment file. The test file gets the
`test_` prefix (pytest convention), but the `02_text_encoder` stem
is shared.

## Why jupytext doesn't work here

- **Tests are binary pass/fail.** Jupytext's `# %%` style is for
  interactive iteration, where you step through and eyeball the
  output. Tests assert: "does this contract hold?" They live in
  pytest, not a notebook.
- **The smoke test is structural, not exploratory.** It's the
  executable proof that your pipeline's X-marker rule was followed.
  Step-through debugging belongs in `experiments/`; assertions
  belong in `tests/`.
- **The pairing must stay 1:1.** One approved design note → one
  experiment script → one test file per category. A second
  `_smoke` file would break that contract and make the workspace
  incoherent when you add regression tests or distribution tests later.

## What happens next

1. **Confirm `experiments/02_text_encoder.py` exists.** If not,
   hand off to `organize-ml-workspace` first.
2. Once it exists, I dispatch to **`smoke-test-ml-pipeline`**, which
   will draft the pytest test at `tests/smoke/test_02_text_encoder.py`.
3. You run the test with `pytest tests/smoke/test_02_text_encoder.py -v`.
   Step through the experiment script interactively in Jupyter if
   you need to debug; the test is just the final assertion.

**Do you have `experiments/02_text_encoder.py` on disk?**
