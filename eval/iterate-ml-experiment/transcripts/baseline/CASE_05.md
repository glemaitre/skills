# CASE_05 — Three-skill implementation chain (no shortcut into evaluate.py)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-ml-experiment/SKILL.md` (1296 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/01_baseline.md` exists, approved.
- `experiments/01_baseline.py` placeholder exists from
  `organize-ml-workspace`.
- `src/<pkg>/pipeline.py`, `features.py`, `data.py`, `evaluate.py`
  do not exist yet.]

Great, the baseline design note is approved. Go ahead and write
`evaluate.py` with `KFold(5)` — it's obviously the right splitter
for this IID tabular task.
```

## Response

I need to stop here and route to `evaluate-ml-pipeline` before writing `evaluate.py`. This is a Stop condition violation.

**The issue:** You've asked me to write `evaluate.py` directly with an assumed CV strategy (`KFold(5)`). The Stop conditions in this skill explicitly forbid this:

> **Three skills, in order, before any code lands in `src/<pkg>/`.** After design-note approval, the implementation step is *not* "let me write the modules"; it is a non-skippable three-skill sequence:
> 1. `build-ml-pipeline` — `pipeline.py`, `features.py`, `data.py`
> 2. `evaluate-ml-pipeline` — `evaluate.py` (cross-validator, metric overrides). **This skill owns the CV-strategy choice and surfaces it to the user via `AskUserQuestion`; writing `evaluate.py` without invoking it is the most common shortcut and means the user never got to pick.**
> 3. `test-ml-pipeline` → `smoke-test-ml-pipeline`

And the forbidden shortcuts table flags this exact pattern:

> **Skipped `evaluate-ml-pipeline` because `KFold(5)` is obviously right for IID tabular** — Even the empty-`split_kwargs` case is a justified pick that the skill exists to surface. Bypassing the skill means the user never got the choice — that's the failure mode, not the splitter value.

**What needs to happen:**

1. **First:** `build-ml-pipeline` to draft `src/<pkg>/pipeline.py`, `features.py`, `data.py` — the pipeline graph declaration with the X-marker.
2. **Then:** `evaluate-ml-pipeline` to surface the CV-strategy options and write `evaluate.py`. Even though `KFold(5)` may be the right choice, *you* don't pick it — the skill surfaces the decision to you, and you confirm or override it via `AskUserQuestion`.
3. **Then:** `test-ml-pipeline` → `smoke-test-ml-pipeline` for the smoke test.
4. **Only then:** this skill assembles `experiments/01_baseline.py`.

The user never got a choice on the CV strategy because it was silently assumed. That's the failure mode this workflow exists to prevent.

**Next action:** Invoke `build-ml-pipeline` to begin the implementation chain.
