# persist-ml-git eval

---

## CASE_01 — Hook said invoke

**User prompt:**
> Persist this EDA turn.

**Assumed workspace state:**
- `python -m skore_skills git end-turn --stage data_analysis` already returned
  `action: invoke`, `reason: persist`, autocommit `on`.
- Dirty paths include `data_analysis/data_analysis.py` and `data_analysis/data_analysis.md`.

**Must do:**
- Run `git status`.
- Stage with `git add` (not `.env` / `.skore`).
- Run `git commit -m` with a one-line subject from this turn.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git push`.
- Call `python -m skore_skills git end-turn` to create the commit.
- Ask about hidden paths when `ambiguous_dotfiles` is empty or
  `reason` is `persist`.

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
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git commit`.
- Run `git push`.

---

## CASE_03 — Triage not installed

**User prompt:**
> Persist this EDA turn.

**Assumed workspace state:**
- `python -m skore_skills git end-turn --stage data_analysis` already returned
  `action: invoke`, `reason: persist`, autocommit `on`.
- `status.skills.triage-ml-task` is `false`.

**Must do:**
- Run `git status` and `git commit -m`.
- Stop after the commit because triage is not installed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent a triage procedure from memory.
- Run `git push`.
