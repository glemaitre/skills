# CASE_01 — Detection of pixi project, install per-manager

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/python-env-manager/SKILL.md` (580 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Project root has `pixi.toml` + `pixi.lock`.
- `skrub` is missing from the env.
- `JOURNAL.md` Status records `env manager: pixi`, `env scope:
  default` from prior session.]

Add skrub to the project's deps.
```

## Response

# Pre-flight (python-env-manager)

- [x] Detection done; manager identified: **pixi**
      Evidence: `pixi.toml` + `pixi.lock` present at project root
- [x] `journal/JOURNAL.md` Status `Workspace decisions` block read
      Evidence: `env manager: pixi` (recorded prior session), `env scope: default` (recorded prior session)
- [x] G-ENV-MGR resolved: **pixi**
      Evidence: JOURNAL.md Status (Workspace decisions, recorded prior session)
- [x] G-ENV-SCOPE resolved: **default** feature
      Evidence: JOURNAL.md Status (Workspace decisions, recorded prior session)
- [x] Install command syntax confirmed: `pixi add <pkg>`
      Evidence: § "Install commands" → pixi subsection
- [x] Package list ready: `skrub`
      Evidence: explicit in this response

---

## Command

```bash
pixi add skrub
```

This adds `skrub` to the default feature in `pixi.toml` and syncs the lock file. Once the command completes, `skrub` will be importable in the environment.
