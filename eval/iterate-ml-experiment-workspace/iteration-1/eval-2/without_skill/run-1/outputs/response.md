I understand the temptation to skip straight to code for a "standard" tabular regression, but I need to enforce the **G-DESIGN gate** here.

**The rule:** No `experiments/NN_*.py` is created or touched until `journal/NN_*.md` exists, is fully filled in, and you've explicitly approved it. This is non-negotiable—the design note is the frozen Method that a postmortem will cite. If it never existed or was never approved, there's no record of what you signed off on.

"Quick" or "standard" does not resolve this gate. That's the **forbidden shortcut** named explicitly in the skill: _User said "quick baseline" → skip G-DESIGN._ It's wrong because the design note is the contract, not an optional luxury.

**What I will do instead:**

I'm reading `data/README.md` now to understand the regression task and derive a goal default. Then I'll auto-draft `journal/01_baseline.md` for you to review and approve. This is **bootstrap mode** (the journal has no history yet), so the baseline is forced, but its defaults come from the sibling skills:

- **Learner default:** consulted from `build-ml-pipeline` (tabular regression → `skrub.tabular_pipeline`).
- **Splitter default:** consulted from `evaluate-ml-pipeline` (typically `KFold` for IID tabular).
- **Metric default:** pulled from `python-api` for what `skore.evaluate` reports by default.

I'll also surface the **config gates that fire in bootstrap**:
- **G-PKG-NAME** — the `src/<pkg>/` import name
- **G-ENV-MGR** — the environment manager
- **G-TABULAR** — pandas vs. polars, Tier 2 picks
- **G-CV-SPLITTER** — cross-validator family (mandatory, even when `split_kwargs` is empty)
- **G-DESIGN** — explicit approval of `journal/01_baseline.md`
- **G-RUN** — "run now" vs. "leave for later"

Once you approve the design note, we hand off to `build-ml-pipeline` to draft the pipeline code, then `evaluate-ml-pipeline` for the evaluation strategy, then `test-ml-pipeline` for the smoke test. Only then does `experiments/01_baseline.py` land.

Let's start: **where should I look for the goal (the target variable, success metric, and dataset summary)?** It should be in `data/README.md` or a similar reference file. Once I read it, I'll draft the design note and surface it for your approval.
