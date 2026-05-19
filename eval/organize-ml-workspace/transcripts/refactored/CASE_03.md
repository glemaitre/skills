# CASE_03 — G-PKG-NAME free-text shortcut

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder named `ml_pricing/`.
- No manifests.]

Scaffold the project. Use whatever name you think is best — go
fast, I don't have a preference.
```

## Response

I'll pause here — I need to respect the operating contract, even with "go fast."

**Stop condition triggered: G-PKG-NAME (mandatory structured ask).**

The default value (folder name → `ml_pricing`) is sensible, but the *pick itself* must come from you via structured question, not from my inference. "No preference" + "go fast" do not waive this gate.

---

## Mandatory question

**What should the package name be (the import name for `src/<pkg>/`)?**

- Default proposal: `ml_pricing` (from your folder name in snake_case)
- Or override with your own choice

Once you confirm, I'll:
1. Record it in `Workspace decisions` (JOURNAL.md Status)
2. Drop `pyproject.toml` with that name
3. Hand off to `python-env-manager` for the manager pick (pixi default)
4. Scaffold the rest (src/, experiments/, journal/, etc.)
5. Hand off to `python-code-style` for ruff setup

Please confirm the package name.
