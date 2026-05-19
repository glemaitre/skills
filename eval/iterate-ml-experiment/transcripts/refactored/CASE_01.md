# CASE_01 — Bootstrap detection

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/iterate-ml-experiment/SKILL_v2.md` (575 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Workspace exists with `src/`, `experiments/`, `journal/` scaffolded
  by `organize-ml-workspace`.
- `journal/JOURNAL.md` is the one-line placeholder dropped by
  `organize-ml-workspace`; History is empty.
- `data/README.md` exists and describes a tabular regression task
  (predict `target` from a mixed-type DataFrame).]

Let's start. Build me a quick baseline for this dataset.
```

## Response

# Iterate ML Experiment — Bootstrap Mode

**Sibling skills (open just-in-time when a step requires):**
- organize-ml-workspace `opened` (confirms scaffold exists)
- data-science-python-stack `pending`
- python-env-manager `pending`
- python-api `pending`
- python-code-style `pending`
- build-ml-pipeline `pending`
- evaluate-ml-pipeline `pending`
- test-ml-pipeline `pending`
- smoke-test-ml-pipeline `pending`
- iterate-from-skore / iterate-from-user `pending`

---

## Pre-flight (Bootstrap)

```
Pre-flight (iterate-ml-experiment):
- [x] `journal/JOURNAL.md` read this turn: placeholder; bootstrap mode
      Evidence: Confirmed empty History in JOURNAL.md
- [x] Mode: bootstrap
      Evidence: Mode picker row 1 — JOURNAL.md missing/placeholder with 0 rows
- [x] Last experiment: n/a — bootstrap
      Evidence: no History rows
- [x] Config gates (G-PKG-NAME, G-ENV-MGR, G-TABULAR, G-CV-SPLITTER)
      will fire this turn
      Evidence: listed below per gate
```

---

## Step 1: Rewrite `JOURNAL.md` from template + derive goal

I've read `data/README.md`: tabular regression task, mixed types, predict `target`.

**Proposed goal (1 sentence):**  
*Minimize RMSE on hold-out test split for predicting `target` from tabular features.*

Is this your goal, or would you like to adjust the metric / split / task framing?

---

## Step 2: Config gates (four questions — no silent defaults)

Bootstrap forces the baseline, but its defaults come from workspace choices. **No clarifying question hints waive these.**

### **G-PKG-NAME** — already set by `organize-ml-workspace`?

If `organize-ml-workspace` ran without asking: it assigned a default import name (likely `src/<pkg>/` inferred from directory structure). 

**Confirm:** What is the import name for your ML package? (e.g., `my_model`, `predictive_app`, `regression_suite`) Is the name your `organize-ml-workspace` chose acceptable?

### **G-ENV-MGR** — environment manager + install scope

**Which environment manager and install scope do you use?**

- **pixi** (reproducible, multi-platform, nix-like; default if not yet chosen) — `pixi add` for deps, `pixi run` for scripts
- **uv** (fast, lightweight, Python-only) — `uv pip install`, `uv run`
- **conda / mamba** (traditional) — `conda install`, `conda run`
- **venv + pip** (minimal) — `pip install`, `python -m` directly

And scope: **workspace-wide** (one `pyproject.toml` or `pixi.toml`) or **per-experiment** (isolation)?

### **G-TABULAR** — tabular library + Tier 2 picks

For mixed-type tabular data, **which library do you prefer?**

- **pandas** (default for regression + mixed types; legacy but solid)
- **polars** (faster, stricter, lazy evaluation; requires explicit schema)

Also, **does your dataset have categorical columns?** If yes, which encoding?

- **ordinal** (integer-encoded, order matters)
- **one-hot** (dummies, unordered categories)
- **target encoding** (rare; skip for baseline)

Baseline default is pandas + one-hot for now; confirm or adjust.

### **G-CV-SPLITTER** — cross-validator family

For this tabular regression task, **which cross-validation strategy?**

- **KFold(5)** (default for IID tabular; 5-fold stratified is standard)
- **TimeSeriesSplit** (if data is temporal — does your README mention order / time?)
- **GroupKFold** (if data has groups / clusters to respect)
- **LeaveOneOut** (tiny dataset only)
- **Holdout only** (no CV; single train / test split)

Baseline default is `KFold(5)` for IID; confirm or adjust. **This choice is non-negotiable even for a "quick" baseline — you get to pick it.**

---

## Next steps (once gates are answered)

Once you answer the four gates:

1. I'll auto-draft `journal/01_baseline.md` with defaults from the three skills (`build-ml-pipeline`, `evaluate-ml-pipeline`, `python-api`).
2. You'll approve or amend the design note.
3. We hand off to the three-skill chain (`build-ml-pipeline` → `evaluate-ml-pipeline` → `test-ml-pipeline` → smoke test).
4. Then `experiments/01_baseline.py` assembles, and **G-RUN** asks: run now or leave for later.

**Please answer the four gates above (G-PKG-NAME, G-ENV-MGR, G-TABULAR, G-CV-SPLITTER).**
