# CASE_05 — Three-skill implementation chain (no shortcut into evaluate.py)

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/iterate-ml-experiment/SKILL_v2.md` (575 lines)

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

I appreciate the enthusiasm, but I need to **pause here and invoke `evaluate-ml-pipeline` before touching `evaluate.py`**, even though `KFold(5)` feels right.

Here's why: § 3's **non-skippable three-skill chain** and the forbidden-shortcut table both flag this exact move. The skill `evaluate-ml-pipeline` **owns the CV-strategy decision and surfaces it via `AskUserQuestion`** — bypassing it is the named shortcut that means *the user never got the choice*.

Even when `KFold(5)` is "obviously right" for IID tabular data, the skill exists to:
1. Confirm the data *is* IID (not temporal, spatial, grouped).
2. Surface alternative split strategies (`StratifiedKFold`, holdout, etc.) if there are hidden reasons.
3. Document the choice with a citation (`skore` defaults, a paper, domain knowledge).
4. Pick `split_kwargs` (empty is a justified pick, not a silent default).

**What I'll do instead:**

- **Open `evaluate-ml-pipeline` now** (add to my read-set tracker as opened).
- **Follow its § "CV-strategy decision" section** — fire the structured ask, present alternatives, let you pick.
- Only **after** that skill returns a choice do I write `evaluate.py`.

Then the chain is:
1. `build-ml-pipeline` → `pipeline.py`, `features.py`, `data.py` ✓
2. **`evaluate-ml-pipeline` (starting now)** → `evaluate.py`
3. `test-ml-pipeline` → smoke test

**One moment — let me read `evaluate-ml-pipeline` and come back with the CV-strategy question.**
