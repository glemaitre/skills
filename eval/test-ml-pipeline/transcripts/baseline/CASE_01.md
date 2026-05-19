# CASE_01 — Standard smoke-test dispatch (post-approval)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/test-ml-pipeline/SKILL.md` (217 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_text_encoder.md` exists with status `approved`.
- `experiments/02_text_encoder.py` exists (scaffold from
  `organize-ml-workspace`).
- `tests/smoke/` exists, empty.
- `pytest` is on the manifest.]

The design note `journal/02_text_encoder.md` was just approved.
Wire the smoke test.
```

## Response

```
Pre-flight (test-ml-pipeline):
- [x] `journal/02_text_encoder.md` exists and is at least `approved`
- [x] `experiments/02_text_encoder.py` exists with the matching stem
- [x] Test category picked: smoke
- [x] Subskill dispatched: `smoke-test-ml-pipeline`
- [x] Test file stem decided: `tests/smoke/test_02_text_encoder.py`
- [x] pytest is on the project's dependency manifest (per
      `data-science-python-stack` § Tier 1)
```

---

**Action: placing empty test file and handing off to `smoke-test-ml-pipeline`.**

I've created:

```python
# tests/smoke/test_02_text_encoder.py
"""Smoke test for experiment 02_text_encoder.

This test asserts the pipeline runs end-to-end without error
and produces outputs matching the contract in journal/02_text_encoder.md.
"""

import pytest


def test_02_text_encoder():
    """
    TODO: filled in by smoke-test-ml-pipeline.
    
    Smoke test for 02_text_encoder experiment.
    """
    pass
```

---

**Now handing off to `smoke-test-ml-pipeline`.**

The empty scaffold is in place with pytest scaffolding. The stem
`02_text_encoder` is paired with both the journal and the experiment
script. 

`smoke-test-ml-pipeline` now owns:
- Reading the design note in `journal/02_text_encoder.md` to extract
  the contract (outputs, schema, any early-warning invariants).
- Constructing fixtures to wire the pipeline.
- Writing assertions that the experiment produces those outputs.
- Ensuring the test runs before the iteration can flip to `done`.

Take it away, `smoke-test-ml-pipeline`.
