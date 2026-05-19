# CASE_05 — Iterate on an existing experiment: ask new vs edit

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_text_encoder.md`, `experiments/02_text_encoder.py`,
  `tests/smoke/test_02_text_encoder.py` all exist and the
  experiment is `done` in JOURNAL.md.]

Let's iterate on `02_text_encoder`. Tweak the encoder config.
```

## Response

I need to pause here and ask before proceeding.

**AskUserQuestion:**

> Should this iteration be:
>
> 1. **In-place edit** of `experiments/02_text_encoder.py` — overwrites the prior result under the same key (`"02_text_encoder"`) in the skore Project?
> 2. **New experiment file** — `03_text_encoder_v2.py` (or similar) — creates a fresh entry in the Project for comparison?

**Important note:** In-place edits will overwrite the prior report in `reports/` under the same key. If you want to keep the baseline result for comparison, new file is safer.

Once you confirm, I'll:
- Open the matching design note (`journal/02_text_encoder.md`) for you to revise the encoder config spec.
- **After design-note approval**, route the code tweak to `iterate-ml-experiment` § 3 and the smoke test to `smoke-test-ml-pipeline`.

Which approach?
