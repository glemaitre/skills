---
name: persist-ml-git
description: >
  Persist the current loop stage with the real git CLI when the
  end-turn hook says invoke. Trigger after
  `python -m skore_skills git end-turn` returns action invoke, or
  when the user asks to commit this turn's work.
---

# Persist ML Git

The hook already ran this turn. Follow its JSON. Run `git` yourself.

1. If `action` is `skip`, stop. Do not nag. Load `triage-ml-task`.
2. If `reason` is `resolve-dotfiles`, ask once which hidden paths
   to keep. Then
   `python -m skore_skills git ignore-merge --keep <path>` or leave
   them ignored. Never keep `.env` or `.skore`.
3. Run `git status`. Stage only non-secret, non-ignored paths:
   `git add -- <paths>`. Never `.env` or `.skore`.
4. Commit with a **one-line** subject from this turn's files and
   intent: `git commit -m "…"`. Do not use a canned stage slogan.
5. Load `triage-ml-task`.

## Stop conditions

- Do not `git push`, amend, rebase, or `git config`.
- Do not invent a commit when the hook was `skip` (`off`,
  `unanswered`, `no_repo`, `clean`).
- Do not call `python -m skore_skills git end-turn` to perform the
  commit; that command only prints facts.
