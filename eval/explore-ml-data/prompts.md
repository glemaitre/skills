# explore-ml-data eval

---

## CASE_01 — End of turn uses git hook

**User prompt:**
> EDA is done. Close the turn.

**Assumed workspace state:**
- `data/eda.md` was just written.

**Must do:**
- Name `python -m skore_skills git end-turn --stage eda`.
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Run `git commit` in this skill.
- Run `git push`.
