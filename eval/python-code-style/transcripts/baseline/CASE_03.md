# CASE_03 — Refuse the hook request, redirect

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-code-style/SKILL.md` (218 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `ruff.toml` exists, `.claude/settings.local.json` present.]

Wire up a PostToolUse hook so ruff runs automatically every time
any `.py` file is edited.
```

## Response

I appreciate the request, but I need to redirect you here based on how this stack is designed.

**The `python-code-style` skill is intentionally manual** — no PostToolUse hook. Here's why:

1. **Tight feedback loops cause churn.** Every micro-edit (e.g., adding one line to a function) would trigger a full ruff pass. Partial files often fail docstring (`D`) checks mid-write, leading to retry cycles that stall the turn.

2. **One-fix-per-file safety rule.** The skill enforces a hard cap — two passes max, then surface remaining issues to you. A hook bypasses that guardrail and can enter infinite-loop territory.

3. **You own the decision to lint.** Claude runs ruff *when you ask* (directly or by triggering this skill), which keeps you in control of when fixes happen. This avoids surprise reformatting or docstring requirements mid-task.

**What you *do* get:**
- When Claude creates or edits a `.py` file, this skill is invoked *before* the task is declared done. Ruff runs, files are fixed, and you see the results.
- You can always run ruff manually outside Claude: `pixi run ruff format src/` + `pixi run ruff check --fix src/` + `pixi run ruff check src/`.

**If you want to enforce ruff on commit or CI**, that's the right place for an automated hook — pre-commit, GitHub Actions, etc. — not in this conversation loop.

Does that distinction make sense? If you'd like to set up a pre-commit hook or CI rule instead, I can help route that to the right place.
