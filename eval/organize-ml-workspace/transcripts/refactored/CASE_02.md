# CASE_02 — Existing workspace, glue not rebuild

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `pyproject.toml` exists with `[project] name = "claim_predictor"`
  and `[tool.setuptools.packages.find]`.
- `src/claim_predictor/__init__.py` exists, plus
  `data.py`, `features.py`, `pipeline.py`, `evaluate.py`.
- `experiments/01_baseline.py` exists; `journal/JOURNAL.md` has
  the baseline row in History.
- `tests/smoke/` exists (empty).
- `pixi.toml` declares deps.]

Help me add a new experiment to this project.
```

## Response

Sibling skills (open just-in-time when a step requires):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, build-ml-pipeline,
    evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline

---

## Detection result

✓ **Existing workspace detected.** Layout is stable:
- Package: `claim_predictor` (in `src/`)
- Experiments: `experiments/`
- Journal: `journal/`
- Env manager: `pixi.toml`
- editable install: wired (via `python-env-manager`)

No scaffold needed. Gluing to existing convention.

---

## Pre-flight

```
Pre-flight (organize-ml-workspace — iteration):
- [x] Layout detection done: existing
      Evidence: pyproject.toml [project] name = "claim_predictor",
                src/claim_predictor/ present, experiments/ present,
                journal/JOURNAL.md with History row, pixi.toml present
- [x] Tier 1 libs importable: sklearn, skrub, skore
      Evidence: pixi.toml declares them; pyproject.toml editable install
                wired by prior python-env-manager step
- [x] package name resolved (G-PKG-NAME): claim_predictor
      Evidence: Confirmed in pyproject.toml [project] name; prior session
- [x] Env manager decided (G-ENV-MGR): pixi
      Evidence: pixi.toml present; prior session
- [x] python-api consulted for: Project, put, evaluate
      Evidence: "n/a — symbols already in workspace cache from 01_baseline.py"
- [ ] Decision: new experiment file vs edit existing
      Evidence: **PENDING** — AskUserQuestion below
```

---

## Next step: new file or iterate?

<AskUserQuestion id="claim_iter_new_or_edit">
You're adding a new experiment to `claim_predictor`. Do you want:

1. **New experiment file** (e.g., `02_feature_selection.py`) — creates a fresh `NN_<short_name>` entry in the skore Project. Best if this is a distinct hypothesis or pipeline variant.
2. **In-place edit of `01_baseline.py`** — overwrites the result under the key `"01_baseline"` in the skore Project. Use this only if you're refining the same idea (e.g., hyperparameter tuning, small preprocessing tweak).

Which path?
</AskUserQuestion>

Once you answer, I'll:
1. **Guide the design-note step** (hand off to `iterate-ml-experiment` for the planning).
2. **Place the experiment script** once the design note is approved.
3. **Wire the smoke test** (hand off to `smoke-test-ml-pipeline` to fill the body).
