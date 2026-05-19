# CASE_01 — Fresh workspace bootstrap

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder (no `pyproject.toml`, no `src/`, no `experiments/`,
  no `journal/`).
- No `data/`, no `pixi.toml`.]

Set up a fresh ML workspace in this folder. Tabular regression.
```

## Response

# Fresh ML Workspace Setup

**Sibling skills tracker:**
```
Sibling skills (open just-in-time when a step requires):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, build-ml-pipeline,
    evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline
```

---

## Pre-flight

```
Pre-flight (organize-ml-workspace):
- [ ] `Workspace decisions` in `journal/JOURNAL.md` Status checked
- [ ] Tier 1 mandatory libs importable: sklearn, skrub, skore
- [ ] Layout detection done: fresh
- [ ] Tabular library decided (G-TABULAR)
- [ ] Env manager decided (G-ENV-MGR)
- [ ] Package name resolved (G-PKG-NAME)
- [ ] `pyproject.toml` present; editable install wired
- [ ] python-api consulted for: Project, put, evaluate
- [ ] Decision: new experiment file vs edit existing
- [ ] `journal/` scaffolded with placeholder JOURNAL.md
```

---

## Gate 1: Tabular library (G-TABULAR)

You've specified **tabular regression**. Which tabular library for data handling and preprocessing?

<AskUserQuestion>
id: Q-TABULAR-001
question: >
  For tabular regression, which structured-data library?
  
  - **pandas** (default, familiar, broad ecosystem)
  - **polars** (faster, lazy evaluation, newer API)
  - No strong preference (I'll use pandas as default)
  
  This choice goes into `Workspace decisions` and affects
  `data.py` loader signatures.
answer_type: choice
options:
  - pandas
  - polars
  - no_preference
</AskUserQuestion>

---

## Gate 2: Environment manager (G-ENV-MGR)

I'll hand off to **`python-env-manager`** for the install strategy:

**→ Open `python-env-manager` SKILL.MD now**

After you've worked through that skill (including Tier 1 + tabular library install), return here with:
- **Which manager** (pixi / uv / poetry / micromamba)?
- **Evidence** that sklearn, skrub, skore are importable.

---

## Gate 3: Package name (G-PKG-NAME)

Once G-ENV-MGR is confirmed, I'll ask:

<AskUserQuestion>
id: Q-PKG-NAME-001
question: >
  Package import name for `src/<pkg>/`?
  
  (The folder name in snake_case is proposed; you can override.)
  What should `from <pkg>.pipeline import build_learner` resolve to?
answer_type: text
placeholder: "e.g., ml_regression, tabular_model, price_predictor"
</AskUserQuestion>

---

## After gates pass → scaffold steps

Once all three gates are locked in (with Evidence), I will:

1. ✓ Drop `pyproject.toml` (with `<pkg>` substituted)
2. ✓ Create `src/<pkg>/` with skeletons:
   - `__init__.py` (PROJECT_ROOT)
   - `data.py` (loaders)
   - `features.py` (transformers)
   - `pipeline.py` (learner)
   - `evaluate.py` (CV strategy)
3. ✓ Create `experiments/01_baseline.py` from template
4. ✓ Create empty `tests/smoke/`
5. ✓ Create `journal/` with placeholder `JOURNAL.md`
6. ✓ Create `overview/summary.md` (placeholder)
7. ✓ Create empty `scratch/`
8. ✓ Create empty `reports/`
9. ✓ Touch `.gitignore`
10. ✓ Hand off to `python-code-style` for ruff config + first pass
11. ✓ Hand off to `iterate-ml-experiment` for design-note work

---

**Next: Answer the tabular library question above, then invoke `python-env-manager`.**
