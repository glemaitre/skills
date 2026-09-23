# explore-ml-directions eval

---

## CASE_01 — Menu lists only installed sources

**User prompt:**
> What should we explore for the next experiment?

**Assumed workspace state:**
- `status.skills.iterate-from-user` is `true`.
- `status.skills.iterate-from-literature` is `false`.
- `status.skills.iterate-from-skore` is `true`.
- `status.skills.manage-ml-backlog` is `true`.
- `python -m skore_skills model choices` returned one Backlog row, B1.

**Must do:**
- Name `python -m skore_skills status`.
- AskUserQuestion with the installed sources only: user idea,
  mine the last audit, and the Backlog row. One pick.

**Must NOT do:**
- Offer literature search.
- Pick a source for the user.
- Write `journal/` or a design note.
- Search the web or read an audit digest in this skill.

---

## CASE_02 — No installed sources returns to triage

**User prompt:**
> Explore ideas for the next experiment.

**Assumed workspace state:**
- `iterate-from-user`, `iterate-from-literature`,
  `iterate-from-skore`, and `manage-ml-backlog` are all `false`
  in `status.skills`.
- `status.skills.triage-ml-task` is `true`.

**Must do:**
- Say in one line that no source skill is installed.
- Load `triage-ml-task`.

**Must NOT do:**
- Invent a user-idea, literature, audit, or backlog procedure.
- Write `journal/`.

---

## CASE_03 — Confirmed proposal asks Draft, Park, or Stop

**User prompt:**
> [iterate-from-user returned a confirmed Proposal for a monotonic
> target transform.]
> Hand it back.

**Assumed workspace state:**
- The child returned a confirmed Proposal.
- `status.skills.model-ml-pipeline` is `true`.
- `status.skills.manage-ml-backlog` is `true`.
- `status.skills.triage-ml-task` is `true`.

**Must do:**
- AskUserQuestion once: Draft, Park, or Stop.

**Must NOT do:**
- Write `journal/` or a design note in this skill.
- Pick Draft, Park, or Stop for the user.
- Load `model-ml-pipeline` before the user picks Draft.

---

## CASE_04 — Question-only return re-shows the source menu

**User prompt:**
> [iterate-from-user answered a project question and returned no
> Proposal.]
> Continue.

**Assumed workspace state:**
- No Proposal and no Backlog candidate rows were returned.
- `status.skills.iterate-from-user` is `true`.
- The other source skills are `false`.

**Must do:**
- Re-show the source menu.

**Must NOT do:**
- Ask Draft, Park, or Stop.
- Emit a Proposal.
