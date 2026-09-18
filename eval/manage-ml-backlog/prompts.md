# manage-ml-backlog eval

---

## CASE_01 — Record outcome into History

**User prompt:**
> The 01_baseline run finished. Record it.

**Assumed workspace state:**
- Audit digest exists with a headline ROC-AUC.
- Smoke tests passed.
- History row for `01_baseline` is `running`.

**Must do:**
- Name `python -m skore_skills status`.
- Copy the headline result into the History row and ask triage.
- Name `python -m skore_skills git end-turn --stage backlog`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Invent a metric that is not in the digest or user text.
- Draft `02_*.py` in this turn.
- Run `git commit` in this skill or `git push`.

---

## CASE_02 — Do not implement next experiment

**User prompt:**
> What should we try next?

**Assumed workspace state:**
- One `done` History row and two Backlog rows `B1`, `B2`.

**Must do:**
- Surface Backlog options and ask triage which lever to take.

**Must NOT do:**
- Silently pick `B1`.
- Invent a deleted iterate skill as the session owner.
- Start `build-ml-pipeline`.

---

## CASE_03 — Missing journal index uses packaged shape

**User prompt:**
> Start the experiment backlog for this workspace.

**Assumed workspace state:**
- `journal/` exists but `journal/JOURNAL.md` is missing.

**Must do:**
- Name `python -m skore_skills scaffold --journal` as the
  initialization command.
- State that the packaged index provides Status, Data understanding,
  History, and Backlog.
- Return to triage after initialization.

**Must NOT do:**
- Paste a `JOURNAL.md` body or markdown fence. Naming
  `scaffold --journal` on a no-tools turn counts; do not
  reconstruct the file.
- Invent a deleted iterate skill.
- Draft or implement an experiment in this turn.
