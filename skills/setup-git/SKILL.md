---
name: setup-git
description: >
  Set up git for an ML workspace after scaffolding. Trigger when the
  user asks to initialize version control, add ignore rules, or make
  the first commit. This action owns first-time git setup only.
---

# Set Up Git

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (skip autocommit ask if already on/off)
- [ ] git init if no .git
- [ ] git ignore-merge (+ --decide / --keep if resolve-dotfiles)
- [ ] git.autocommit ask if null
- [ ] first commit only if autocommit is on and no HEAD yet
```

## Sequence

1. Run `python -m skore_skills status`. If
   `policy.git.autocommit` is already `on` or `off`, do not ask
   that question again.
2. If there is no `.git` directory, run `git init`. Do not run
   `git config`.
3. Run `python -m skore_skills git ignore-merge`.
4. If JSON `ambiguous_dotfiles` is non-empty, ask once which hidden
   paths to keep tracked. Then re-run
   `python -m skore_skills git ignore-merge --decide` plus
   `--keep <path>` for each chosen path (no `--keep` if they keep
   none). Do not re-ask names gone from the next JSON. Never
   `--keep` `.env` or `.skore`.
5. If `policy.git.autocommit` is `null`, ask **once**: should later
   stages persist with `git commit` (`on`) or never (`off`)? Persist
   with `python -m skore_skills policy set git.autocommit on` or
   `off`. That answer is also consent for the first commit.
6. If autocommit is `on` and this repo has no HEAD yet, run
   `git status`. Then `git add -- <paths>` and
   `git commit -m "<one-line subject>"` from this setup turn. Do
   not ask a second time. Never stage `.env`, `.skore`, or raw
   data.
7. If autocommit is `off`, stop after ignore-merge. Do not
   `git commit`.
8. If autocommit is already `on` and HEAD exists, stop after
   ignore-merge. Do not invent another commit. Later stages use
   `python -m skore_skills git end-turn` then `persist-ml-git`;
   when that skill is not installed, those stages report the
   pending paths instead of committing.
9. When `setup-ml-project` dispatched this turn and is in this
   session, return control to it. Otherwise load `triage-ml-task`
   if `status.skills` reports it installed, else stop.

## Stop conditions

- Never overwrite `.gitignore`; `git ignore-merge` unions packaged
  rules.
- Never stage secrets, raw data, `.env`, or `.skore`.
- Never push, create a remote, amend, rebase, or set git identity.
- Do not call `python -m skore_skills git end-turn` to create the
  first commit.
