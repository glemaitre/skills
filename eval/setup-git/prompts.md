# setup-git eval

---

## CASE_01 — First repository, autocommit on

**User prompt:**
> Initialize git here and make the first commit.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `.env` and raw data are present and must remain untracked.
- `policy.git.autocommit` is `null` (never asked).
- The user answers the autocommit question with `on`.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Name `git init`.
- Name `python -m skore_skills git ignore-merge`.
- Ask once whether later stages may autocommit (`on` vs `off`) and
  persist with `python -m skore_skills policy set git.autocommit`.
- After `on`, use `git add` and `git commit -m` without a second
  confirm.

**Must NOT do:**
- Stage `.env` or raw data.
- Ask a second time before the first commit after `on`.
- Push or create a remote.
- Use `python -m skore_skills git end-turn` to create the first
  commit.

---

## CASE_02 — Autocommit already persisted

**User prompt:**
> Git is already initialized. Check ignore rules.

**Assumed workspace state:**
- A git repository exists and already has a HEAD commit.
- `policy.git.autocommit` is already `on`.

**Must do:**
- Run or name `python -m skore_skills git ignore-merge`.
- Skip the autocommit policy question because it is already `on`.

**Must NOT do:**
- Re-ask whether later stages may autocommit.
- Invent another `git commit` on this turn.
- Run `git push`.

---

## CASE_03 — Autocommit off, no first commit

**User prompt:**
> Initialize git here.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `policy.git.autocommit` is `null`.
- The user answers the autocommit question with `off`.

**Must do:**
- Name `git init`.
- Name `python -m skore_skills git ignore-merge`.
- Persist `python -m skore_skills policy set git.autocommit off`.

**Must NOT do:**
- Run `git commit`.
- Run `git push`.
- Use `python -m skore_skills git end-turn` to create a commit.

---

## CASE_04 — Resolve hidden paths

**User prompt:**
> Set up git and keep the `.cursor` folder tracked.

**Assumed workspace state:**
- Scaffolded workspace, not yet a git repository.
- `python -m skore_skills git ignore-merge` returns
  `action: resolve-dotfiles` with `.cursor/` listed.
- `policy.git.autocommit` is already `on`.
- No HEAD yet.

**Must do:**
- Name `python -m skore_skills git ignore-merge`.
- Ask which hidden paths to keep, then re-run
  `python -m skore_skills git ignore-merge --keep .cursor`.
- After autocommit `on` and no HEAD, `git add` and `git commit`.

**Must NOT do:**
- `--keep` `.env` or `.skore`.
- Use `python -m skore_skills git end-turn` to create the first
  commit.
