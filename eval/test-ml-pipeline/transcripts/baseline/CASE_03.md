# CASE_03 — Stem-rule enforcement (no v2 / no _2 suffix)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/test-ml-pipeline/SKILL.md` (217 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_text_encoder.md` exists, approved.
- `experiments/02_text_encoder.py` exists.
- `tests/smoke/test_02_text_encoder.py` exists (current shape).]

The smoke test for `02_text_encoder` needs a major rewrite — the
new assertions don't fit. Create
`tests/smoke/test_02_text_encoder_v2.py` with the new shape.
```

## Response

I need to stop here and hold the line on the stem rule.

## Pre-flight (test-ml-pipeline)

```
Pre-flight (test-ml-pipeline):
- [x] `journal/02_text_encoder.md` exists and is at least `approved`
- [x] `experiments/02_text_encoder.py` exists with the matching stem
- [x] Test category picked: smoke
- [ ] BLOCKED: stem rule violation detected
- [ ] Test file stem decided: CANNOT PROCEED
- [x] pytest is on the project's dependency manifest
```

---

## The issue

**The stem rule is hard.** You asked to create `test_02_text_encoder_v2.py`,
but that violates the 1:1 pairing contract:

```
experiments/02_text_encoder.py
         ↓ (single pairing, one per category)
tests/smoke/test_02_text_encoder.py    ← only this, ever
```

Not `v2`, not `_2`, not `_revised`. One experiment → one test file per category.

---

## What to do instead

The test file `tests/smoke/test_02_text_encoder.py` already exists.
**Edit it in place.** Replace the old assertions with the new ones.
The file stays at the same path; the contract stays 1:1.

Once you've rewritten it, hand the updated test back to
**`smoke-test-ml-pipeline`** — that subskill owns the assertion
bodies, fixture construction, and the validation loop. It will
confirm the new shape is correct before you run pytest.

---

**Ready to proceed with the in-place rewrite?**
