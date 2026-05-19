# test-ml-pipeline eval — golden prompts

Behavioural prompts for the test-ml-pipeline router. Pass = every Must
do ticked, zero Must NOT violated.

---

## CASE_01 — Standard smoke-test dispatch (post-approval)

**User prompt:**
> The design note `journal/02_text_encoder.md` was just approved.
> Wire the smoke test.

**Assumed workspace state:**
- `journal/02_text_encoder.md` exists with status `approved`.
- `experiments/02_text_encoder.py` exists (scaffold from
  `organize-ml-workspace`).
- `tests/smoke/` exists, empty.
- `pytest` is on the manifest.

**Must do:**
- Confirm the approved design note exists.
- Pick test category: **smoke**.
- Decide test file stem: `tests/smoke/test_02_text_encoder.py`.
- Dispatch to **`smoke-test-ml-pipeline`** for the body.
- Mention placing the empty test file + pytest scaffolding
  (one `def test_*():`, empty body, TODO marker).

**Must NOT do:**
- Write assertion bodies in this skill (subskill owns that).
- Overwrite an existing test file (the rule is 1:1 pairing).
- Create a `test_NN_<short_name>_v2.py` variant (stem rule is hard).

---

## CASE_02 — No design note → refuse + hand off

**User prompt:**
> Write the smoke test for `experiments/03_target_transform.py`.

**Assumed workspace state:**
- `experiments/03_target_transform.py` exists (someone wrote it directly).
- `journal/03_target_transform.md` does **not** exist.
- `tests/smoke/` exists.

**Must do:**
- Refuse to create the test file.
- Cite the Stop condition: "No test without an approved design note."
- Hand off back to `iterate-ml-experiment` to author + approve the
  design note first.

**Must NOT do:**
- Create `tests/smoke/test_03_target_transform.py` even as a stub.
- Treat the existence of the script as resolving the design-note
  requirement.

---

## CASE_03 — Stem-rule enforcement (no v2 / no _2 suffix)

**User prompt:**
> The smoke test for `02_text_encoder` needs a major rewrite — the
> new assertions don't fit. Create
> `tests/smoke/test_02_text_encoder_v2.py` with the new shape.

**Assumed workspace state:**
- `journal/02_text_encoder.md` exists, approved.
- `experiments/02_text_encoder.py` exists.
- `tests/smoke/test_02_text_encoder.py` exists (current shape).

**Must do:**
- Refuse to create `test_02_text_encoder_v2.py`.
- Cite the stem rule: pairing is 1:1, the file basename is hard.
- Recommend editing `tests/smoke/test_02_text_encoder.py` in place,
  via the `smoke-test-ml-pipeline` subskill for the new body.

**Must NOT do:**
- Create the `_v2.py` file as written.
- Create `test_02_text_encoder_2.py` (same anti-pattern by
  different syntax).
- Auto-edit the existing file without surfacing the choice.

---

## CASE_04 — Dispatch table: future categories not implemented

**User prompt:**
> The metrics drifted between 02 and 03. Can we lock that in with a
> regression test?

**Assumed workspace state:**
- `journal/03_target_transform.md` exists, approved, done with metrics.
- `tests/smoke/` exists with prior smoke tests.

**Must do:**
- Recognise this as a **regression test** category per the dispatch
  table.
- Surface that `regression-test-ml-pipeline` is **future / not
  implemented in v1**.
- Offer alternatives (e.g. propose a `tests/smoke/` assertion that
  catches the drift indirectly, or note the gap to be filled when
  the regression subskill ships).

**Must NOT do:**
- Silently dispatch to `regression-test-ml-pipeline` as if it exists.
- Default to `smoke-test-ml-pipeline` without flagging the category
  mismatch.
- Author the regression test body inline (this skill is the router,
  not the body owner).

---

## CASE_05 — pytest is the runner (no `# %%` scripts)

**User prompt:**
> Let's just write the smoke test as a jupytext `# %%` script under
> `experiments/02_text_encoder_smoke.py` so I can step through it.

**Assumed workspace state:**
- `journal/02_text_encoder.md` approved.
- `tests/smoke/` exists.

**Must do:**
- Refuse the `# %%` script form for tests.
- Cite the Stop condition: tests are pytest tests, not jupytext.
- Surface the convention split: `experiments/` = `# %%`,
  `tests/smoke/` = pytest.
- Route to `tests/smoke/test_02_text_encoder.py` (pytest scaffolding)
  via `smoke-test-ml-pipeline`.

**Must NOT do:**
- Create `experiments/02_text_encoder_smoke.py`.
- Mix the two conventions.

---

## CASE_06 — Default to smoke when user is open-ended

**User prompt:**
> Should this experiment have a test? It's just a quick baseline.

**Assumed workspace state:**
- `journal/01_baseline.md` approved.
- `experiments/01_baseline.py` exists.
- `tests/smoke/` empty.

**Must do:**
- Recognise the open-ended question.
- Default to **smoke** category (smoke is required at every
  iteration; everything else is opt-in).
- Cite the required-test-per-experiment rule (smoke gate before
  `done`).
- Dispatch to `smoke-test-ml-pipeline`.

**Must NOT do:**
- Treat "just a quick baseline" as waiving the smoke-test
  requirement.
- Skip the test entirely.
- Pick regression / distribution by default.
