# persist-ml-git eval

---

## CASE_01 — Hook said invoke

**User prompt:**
> Persist this EDA turn.

**Assumed workspace state:**
- `python -m skore_skills git end-turn --stage eda` already returned
  `action: invoke`, `reason: persist`, autocommit `on`.
- Dirty paths include `eda/eda.py` and `eda/eda.md`.

**Must do:**
- Run `git status`.
- Stage with `git add` (not `.env` / `.skore`).
- Run `git commit -m` with a one-line subject from this turn.

**Must NOT do:**
- Run `git push`.
- Call `python -m skore_skills git end-turn` to create the commit.

---

## CASE_02 — Hook said skip off

**User prompt:**
> Commit the pipeline changes.

**Assumed workspace state:**
- The end-turn hook returned `action: skip`, `reason: off`.

**Must do:**
- Refuse to commit.
- Load `triage-ml-task` if installed, else stop.

**Must NOT do:**
- Run `git commit`.
- Run `git push`.
