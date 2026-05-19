# CASE_05 — Mixed ambient state (pixi + conda visible)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-env-manager/SKILL.md` (580 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Project root has `pixi.toml` (pixi-managed).
- A conda env named `myenv` is active in the user's shell.
- `pip --version` shows pip from conda's env, not pixi's.]

Install lightgbm.
```

## Response

# Install lightgbm

## Detection & Pre-flight

**STOP: Workspace state mismatch detected.** The project uses pixi (`pixi.toml` present), but your shell shows an active conda env (`myenv`). Before installing lightgbm, we need to clarify: should the package go into pixi's environment or the active conda env?

**Current state:**
- Project manifest: `pixi.toml` (pixi-managed)
- Active shell env: `myenv` (conda)
- `pip` on PATH: conda's pip, not pixi's

Installing into the active conda env would create drift — `pixi install` on the next sync would not see lightgbm, and the manifest wouldn't track it.

---

## Clarification needed (AskUserQuestion)

**Where should lightgbm be installed?**

1. **Into pixi's environment** (recommended — keeps the manifest in sync):
   - First, deactivate the conda env: `conda deactivate`
   - Then use pixi's package manager

2. **Into the active conda env (`myenv`)** (if this is a separate workflow from the pixi project):
   - Continue using conda, but understand this package won't be tracked in `pixi.toml`

Which path should I take?

---

Once you pick, I'll enumerate the existing pixi features (or ask which conda env scope, if conda is your choice) and confirm the install command with you before running it.
