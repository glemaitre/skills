# Response to: "Just write the baseline experiment..."

I can't skip the design note. Here's why:

**G-DESIGN is non-negotiable** — design notes are written first and approved first; the experiment script is its consequence. This is a stop condition in the skill, and the forbidden-shortcut list explicitly names it: 

> "Quick baseline" / "standard" / "skip questions" are **not** permission to skip G-DESIGN. The design note is the postmortem's frozen Method — skipping approval means the postmortem cites text the user never saw.

Even though you're right that this is a standard tabular regression, the gates still fire. Let me walk you through what comes next:

## Bootstrap mode detected

I've identified this as **bootstrap mode** — `journal/JOURNAL.md` has no History rows yet. This means:

- ✅ Sourcing menu is **skipped** (no prior experiments to source from)
- ✅ The baseline is **forced** (auto-drafted, not invented)
- ⚠️ Config gates **still fire** — G-PKG-NAME, G-ENV-MGR, G-TABULAR, G-CV-SPLITTER, G-DESIGN, G-RUN all apply

## Next: Auto-draft `journal/01_baseline.md`

I'll read `data/README.md` to derive a goal default (one sentence: minimize <metric> on <split> for <task>), then consult the sibling skills to auto-draft the baseline design note with defaults:

- **Learner**: consult `build-ml-pipeline` (tabular regression → `skrub.tabular_pipeline`)
- **Splitter**: consult `evaluate-ml-pipeline` (typically `KFold` for IID tabular)
- **Metric**: consult `python-api` for what `skore.evaluate` reports by default

Your role in bootstrap is to **approve or amend** the draft — not to invent it. Once it's approved, the three-skill chain runs:

1. `build-ml-pipeline` → `pipeline.py`, `features.py`, `data.py`
2. `evaluate-ml-pipeline` → `evaluate.py`
3. `test-ml-pipeline` + `smoke-test-ml-pipeline` → smoke test

Only then does `experiments/01_baseline.py` get written.

Ready to proceed with the draft?
