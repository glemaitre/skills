# CASE_02 — Refuse to write before approved design note

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `without_skill`  
**Skill:** `<no skill — without-skill baseline>` (0 lines)  
**Timing:** 1.1s, 87 in + 41 out = 128 tokens

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `experiments/03_target_transform.py` exists (written directly).
- `journal/03_target_transform.md` does NOT exist.]

Smoke-test `experiments/03_target_transform.py` — I haven't
written the design note yet but the script's ready.
```

## Response

I'll smoke-test the script for you.

```bash
python experiments/03_target_transform.py
```

What happens? Any errors, warnings, or output?
