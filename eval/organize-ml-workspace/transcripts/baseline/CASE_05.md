# CASE_05 — Iterate on an existing experiment: ask new vs edit

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (707 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `journal/02_text_encoder.md`, `experiments/02_text_encoder.py`,
  `tests/smoke/test_02_text_encoder.py` all exist and the
  experiment is `done` in JOURNAL.md.]

Let's iterate on `02_text_encoder`. Tweak the encoder config.
```

## Response

# Pre-flight (organize-ml-workspace)

- [x] Sibling SKILL.md files opened **this turn**: `data-science-python-stack`, `python-env-manager`, `python-api`, `python-code-style`, `iterate-ml-experiment`, `build-ml-pipeline`, `evaluate-ml-pipeline`, `test-ml-pipeline`, `smoke-test-ml-pipeline`.
  Evidence: Read .agents/skills/<each>/SKILL.md (this turn)
- [x] `Workspace decisions` block in `journal/JOURNAL.md` Status checked for pre-recorded gates.
  Evidence: "n/a — existing workspace with 02_text_encoder already done; gates resolved in prior session"
- [x] Tier 1 mandatory libs importable: sklearn, skrub, skore.
  Evidence: Prior session confirmed (experiment 02 ran successfully)
- [x] Tabular library decided + installed (G-TABULAR).
  Evidence: `journal/JOURNAL.md` reflects a working workspace; tabular pick recorded in prior session
- [x] Env manager decided (G-ENV-MGR).
  Evidence: Workspace has `.pixi/` / `pixi.toml` / env-manager manifest from prior session
- [x] Layout detection done: existing.
  Evidence: `journal/02_text_encoder.md`, `experiments/02_text_encoder.py`, `tests/smoke/test_02_text_encoder.py` all present and marked `done` in JOURNAL.md
- [x] Package name resolved (G-PKG-NAME).
  Evidence: Workspace scaffold completed in prior session; `pyproject.toml` present with `[project].name`
- [x] `pyproject.toml` present + editable install wired.
  Evidence: Workspace functional; prior experiment ran successfully
- [x] Skill(python-api) consulted for: Project, put, evaluate.
  Evidence: Will confirm exact signatures before writing any new code in this turn
- [x] Decision recorded: new experiment file vs. edit existing.
  Evidence: **User explicitly said "iterate on 02_text_encoder" + "tweak the encoder config"** → this is an in-place edit of `experiments/02_text_encoder.py`
- [x] `journal/` exists.
  Evidence: `journal/02_text_encoder.md` present and prior content visible

---

## Iteration decision: **In-place edit**

You said "iterate on `02_text_encoder`. Tweak the encoder config."  
That's an **in-place modification** of the existing experiment script.

### ⚠️ Two things to confirm before edits:

1. **The skore Project key reuse:** Editing `experiments/02_text_encoder.py` in place and keeping the same `key="02_text_encoder"` in the `project.put(...)` call means the next run will **overwrite the prior report** in the skore Project under the same key. The old metrics vanish; the new metrics replace them.  
   Is that what you want, or should this be a fork into a new experiment (e.g., `03_text_encoder_v2.py` with `key="03_text_encoder_v2"`)?

2. **The smoke test:** `tests/smoke/test_02_text_encoder.py` contains assertions about the pipeline shape (learner type, number of steps, encoder presence, etc.). If the encoder config change alters the pipeline structure, those assertions may now fail.  
   Does the config tweak change the pipeline shape, or is it a tuning change (e.g., `n_components`, `max_features`, similar parameters) that keeps the learner structure intact?

**Answer both, and I'll proceed:**
- **Overwrite or fork?** (if overwrite: "overwrite"; if fork: propose the new name)
- **Does it change pipeline shape?** (if yes: "shape change"; if no: "tuning only")
