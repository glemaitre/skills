# setup-git eval

---

## CASE_01 — First repository

**User prompt:**
> Initialize git here and make the first commit.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `.env` and raw data are present and must remain untracked.
- `policy.git.autocommit` is `null` (never asked).

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Name `git init`.
- Name `python -m skore_skills git ignore-merge`.
- Ask once whether later stages may autocommit (`on` vs `off`) and
  persist with `python -m skore_skills policy set git.autocommit`.
- Ask before creating the first commit, then use `git add` and
  `git commit -m`.

**Must NOT do:**
- Stage `.env` or raw data.
- Commit, push, or create a remote without confirmation.
- Use `python -m skore_skills git end-turn` to create the first
  commit.

---

## CASE_02 — Autocommit already persisted

**User prompt:**
> Git is already initialized. Check ignore rules.

**Assumed workspace state:**
- A git repository exists.
- `policy.git.autocommit` is already `on`.

**Must do:**
- Run or name `python -m skore_skills git ignore-merge`.
- Skip the autocommit policy question because it is already `on`.

**Must NOT do:**
- Re-ask whether later stages may autocommit.
- Run `git push`.
