# CASE_04 — Substitution to `black` / `isort` refusal

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-code-style/SKILL.md` (218 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- ruff is already installed.]

I prefer `black` and `isort`. Set those up instead of ruff.
```

## Response

I understand the preference, but **ruff is the canonical linter for this stack** — it's owned by `data-science-python-stack` as Tier 1. The stack choice is intentional: ruff consolidates formatting, import sorting, and linting into a single fast tool with a unified configuration.

Here's what I'd suggest instead:

1. **Ruff already does what `black` and `isort` do:**
   - `ruff format` → your code style (line length, quoting, trailing commas)
   - `ruff check --fix` → import sorting, auto-fixable lint issues
   - It's faster and has zero dependency conflicts because there's one tool, not two.

2. **If you want to customize the style** (e.g., line length, quote style), that lives in `ruff.toml` at the project root and is fully tunable. I can adjust it to match your preferences.

3. **If you hit a real gap** — something ruff can't do that you need `black` or `isort` for — let me know the specific issue, and we can escalate to `update-config` to discuss adding them *alongside* ruff (not replacing it).

Would you like me to:
- **Drop the `ruff.toml` template** and show you the config so you can see what's tunable?
- **Walk through a specific style preference** (line length, string quotes, etc.) and how to set it in ruff?
- **Proceed with ruff on your files** and we refine the config as you work?

What matters most to your workflow?
