---
name: setup-git
description: >
  Set up git for an ML workspace after scaffolding. Trigger when the
  user asks to initialize version control, add ignore rules, or make
  the first commit. This action owns first-time git setup only.
---

# Set Up Git

1. Run `python -m skore_skills status`. If
   `policy.git.autocommit` is already `on` or `off`, do not ask
   that question again.
2. If there is no `.git` directory, run `git init`. Do not run
   `git config`.
3. Run `python -m skore_skills git ignore-merge`.
4. If JSON `action` is `resolve-dotfiles`, ask once which hidden
   paths to keep tracked, then re-run
   `python -m skore_skills git ignore-merge --keep <path>`. Leave
   the rest ignored. Never `--keep` `.env` or `.skore`.
5. If `policy.git.autocommit` is `null`, ask **once**: should later
   stages persist with `git commit` (`on`) or never (`off`)? Persist
   with `python -m skore_skills policy set git.autocommit on` or
   `off`.
6. Run `git status`. Ask before the **first** commit. After
   confirmation, `git add -- <paths>` then
   `git commit -m "<one-line subject>"` from this setup turn.
   Later stages use `python -m skore_skills git end-turn` then
   `persist-ml-git`.
7. Load `triage-ml-task`.

## Stop conditions

- Never overwrite `.gitignore`; `git ignore-merge` unions packaged
  rules.
- Never stage secrets, raw data, `.env`, or `.skore`.
- Never push, create a remote, amend, rebase, or set git identity.
- Do not call `python -m skore_skills git end-turn` to create the
  first commit.
