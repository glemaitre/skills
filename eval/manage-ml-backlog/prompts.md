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

**Must NOT do:**
- Invent a metric that is not in the digest or user text.
- Draft `02_*.py` in this turn.

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
- Load `iterate-ml-experiment` as the session owner.
- Start `build-ml-pipeline`.
