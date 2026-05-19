# CASE_03 — Refuse the hook request, redirect

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/python-code-style/SKILL.md` (263 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `ruff.toml` exists, `.claude/settings.local.json` present.]

Wire up a PostToolUse hook so ruff runs automatically every time
any `.py` file is edited.
```

## Response

I appreciate the request, but I need to redirect you here: **this skill explicitly does not configure PostToolUse hooks for ruff.** That's a deliberate design decision, not an oversight.

Here's why the default is manual:

1. **Tight loop friction.** Every micro-edit (adding a parameter, fixing a typo in a docstring) triggers a full ruff pass. The edit → lint → fix cycle becomes chatty and can stall mid-task.
2. **Partial-file D-rule failures.** While Claude is writing a function body, the docstring may be incomplete. A hook fires mid-write and reports "missing Parameters section" — but Claude was about to add it next. That noise breaks flow.
3. **Retry spirals.** If Claude's first fix doesn't resolve a warning, the hook fires again on the same file, potentially re-triggering the same diagnostic. The **one-fix-per-file rule** in this skill is the anti-infinite-loop guardrail; a hook bypasses it.

**The manual approach works:** Claude finishes editing a file, then runs ruff itself (3 commands: format → check --fix → check). Done in one pass, surfaces any remaining issues cleanly.

---

**If you genuinely need automation later** — for instance, a CI pipeline that lints staged files — that's a job for **`update-config`** (the skill that owns config-file edits). It can wire up a pre-commit hook, a GitHub Actions workflow, or a Makefile target.

For now, the default stays: you write code, I run ruff on it before we declare the task done. No hook.
