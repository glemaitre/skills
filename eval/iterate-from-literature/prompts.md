# iterate-from-literature eval

---

## CASE_01 — Query is rewritten before search

**User prompt:**
> What does the literature say about improving the California
> housing model?

**Assumed workspace state:**
- `JOURNAL.md` Status goal is continuous housing-value regression.
- The dataset name is California housing.

**Must do:**
- Rewrite the query as a problem class before searching.
- Search scientific or technical sources and fetch primary pages.
- Show two to four directions, each with a URL and a claim, and
  ask the user to pick, narrow, or stop.
- Name `scratch/research/direction-<slug>.md` as the note to write.

**Must NOT do:**
- Put the dataset proper name, `fetch_california_housing`, or a
  Kaggle slug in the search query.
- Rank a winner or say which direction to run next.
- Emit a `Proposal (` block before the user picks and confirms.
- Write `journal/` or a design note.
- Load `research-ml-practice`.

---

## CASE_02 — Picked direction confirms, then returns a Proposal

**User prompt:**
> Use the second direction.

**Assumed workspace state:**
- This turn already showed directions. The user picked one.
- A fetched page supports the claim.

**Must do:**
- Show the plain-text confirmation restatement and wait.
- After an explicit yes, return a Proposal whose Source is the
  URL and the claim. Transfer risks stay in Open gaps.

**Must NOT do:**
- Emit a `Proposal (` header before yes.
- Author acceptance criteria.
- Add a package in this skill.

---

## CASE_03 — Search cannot run

**User prompt:**
> Look up papers on censored regression for tabular targets.

**Assumed workspace state:**
- Web search and fetch tools are unavailable this turn.

**Must do:**
- Say that search cannot run and stop.

**Must NOT do:**
- Invent papers, URLs, or claims.
- Emit a Proposal.
- Write `journal/`.
