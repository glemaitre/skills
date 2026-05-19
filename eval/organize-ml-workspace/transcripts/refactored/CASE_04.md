# CASE_04 — Pre-emptive experiment file creation

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `refactored`  
**Skill:** `skills/organize-ml-workspace/SKILL.md` (440 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- Empty folder, fresh scaffold.]

Scaffold the workspace and write the baseline experiment
`experiments/01_baseline.py` so we can run it right away.
```

## Response

I'll scaffold the workspace and prepare to write the baseline experiment. Let me start with the pre-flight checklist and detection.

```
Sibling skills (open just-in-time when a step requires):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, build-ml-pipeline,
    evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline
```

---

## Detection & Pre-flight

**Reading project root:** Empty folder detected. Fresh scaffold path.

Before proceeding, I need to resolve three gates:

<AskUserQuestion id="gate_tabular">
**G-TABULAR:** Which tabular library should the workspace use—**pandas** or **polars**?

This determines what's installed on the manifest and what `data.py` imports.
</AskUserQuestion>

<AskUserQuestion id="gate_pkg_name">
**G-PKG-NAME:** What should the package name be (the import name, lives under `src/<pkg>/`)?

*Proposed default:* If the folder is named `my_project`, use `my_project`. You can override.
</AskUserQuestion>

<AskUserQuestion id="gate_env_manager">
**G-ENV-MGR:** Which environment manager?

- **pixi** (recommended; fastest, no system Python required)
- **uv** (fast, needs Python ≥3.10 on system)
- **poetry** (slower, familiar to some teams)
- **conda/mamba** (slower, widest compatibility)

*Proposed default:* pixi.
</AskUserQuestion>

---

Once you confirm those three, I'll proceed through the 13-step flow:

1. ✓ Detection done (fresh).
2. G-PKG-NAME answer → record.
3. G-TABULAR answer → record.
4. G-ENV-MGR answer → record.
5. Drop `pyproject.toml` with `src/<pkg>/`.
6. Create `src/<pkg>/` with skeleton modules.
7. Create `experiments/` with seed `01_baseline.py` (but **not yet** filled with real code).
8. Create empty `tests/smoke/`.
9. Create `journal/` with placeholder `JOURNAL.md`.
10. Create `overview/` with placeholder `summary.md`.
11. Create empty `scratch/`.
12. Create empty `reports/`.
13. Touch `.gitignore`.
14. Hand off to `python-code-style` for ruff setup.
15. Hand back for design-note seeding.

**Key point:** The experiment script `01_baseline.py` will be scaffolded (imports, skeleton structure) but **not filled with learner/data specifics** — that comes after you design the experiment in `journal/01_baseline.md` via `iterate-ml-experiment`.

---

Please answer the three gates above, and I'll proceed.
