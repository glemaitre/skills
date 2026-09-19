# research-ml-practice eval

---

## CASE_01 — Intake when concern is missing

**User prompt:**
> Research this for me.

**Assumed workspace state:**
- Caller did not supply a concern or mode survey.
- JOURNAL names no specific question.

**Must do:**
- AskUserQuestion survey first vs I will name a concern
  (neither recommended).

**Must NOT do:**
- Start a depth web search with an empty concern.
- Offer EDA Open questions as a closed concern menu as if
  they were literature.
- Drop a column or rewrite raw data.

---

## CASE_02 — Skip intake when concern is supplied

**User prompt:**
> Research whether a 0.97 Pearson with the target is leakage on
> this regression table. Domain is real estate.

**Assumed workspace state:**
- Concern and domain are in the prompt.

**Must do:**
- Run distinct-angle **depth** searches (practice, implementation,
  pitfalls at least).
- Tag each candidate with a lane (`measure` / `declare` /
  `evaluate` / `confirm`).
- Write `scratch/research/<slug>.md`.
- Return the path and a one- or two-sentence finding to the
  caller.

**Must NOT do:**
- Re-ask domain and concern.
- Run a survey first.
- Drop the correlated column.
- Run `pixi add` / `uv add`.
- Write `data_analysis.md` or the design note.
- Paste the full scratch note into chat.

---

## CASE_03 — Boundaries

**User prompt:**
> Research whether I should drop customer_id.

**Assumed workspace state:**
- Concern is dropping an identifier column.

**Must do:**
- Rank dropping as a *candidate* for the pipeline skill, not an
  action on `data/`.

**Must NOT do:**
- Modify raw data files.
- Pick the final learner.
- `git end-turn` or `git commit`.
- Write `data_analysis.md`.

---

## CASE_04 — Open survey proposes concerns

**User prompt:**
> Survey the literature for this real-estate regression table.
> Do not pick a concern yet.

**Assumed workspace state:**
- Caller passed mode survey (or equivalent open research).
- No named concern.

**Must do:**
- Run survey-angle searches (practice, pitfalls, what to
  check) without a named concern.
- Write `scratch/research/survey-<slug>.md` with sourced
  proposed concerns.
- Return the path and a one- or two-sentence finding.

**Must NOT do:**
- Write a ranked `measure` / `declare` action table in that
  note.
- Offer Open questions as the concern list before searching.
- Write `data_analysis.md` or the design note.
- Paste the full scratch note into chat.
