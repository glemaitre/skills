# research-ml-practice eval

---

## CASE_01 — Intake when concern is missing

**User prompt:**
> Research this for me.

**Assumed workspace state:**
- Caller did not supply a concern.
- JOURNAL names no specific question.

**Must do:**
- AskUserQuestion for the specific concern before searching.

**Must NOT do:**
- Start web search with an empty concern.
- Drop a column or rewrite raw data.

---

## CASE_02 — Skip intake when concern is supplied

**User prompt:**
> Research whether a 0.97 Pearson with the target is leakage on
> this regression table. Domain is real estate.

**Assumed workspace state:**
- Concern and domain are in the prompt.

**Must do:**
- Run distinct-angle searches (practice, implementation,
  pitfalls at least).
- Produce ranked candidates with confidence and sources.
- Write `scratch/research/<slug>.md`.

**Must NOT do:**
- Re-ask domain and concern.
- Drop the correlated column.
- Run `pixi add` / `uv add`.

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
