# model-ml-pipeline eval

---

## CASE_01 — Approved model implementation

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.
- Workspace is scaffolded (`has_src` and `has_journal` true).

**Must do:**
- Name `python -m skore_skills status`.
- Resume the approved stem directly; do not show the starting
  choices menu.
- Preview the broad sequence as local pipeline preparation, small
  real-data smoke fit/predict, optional full-dataset evaluation,
  then read-only audit; leave each detailed compute preview to
  its child skill and do not invent minute estimates.
- Dispatch `build-ml-pipeline` (do not load
  `smoke-test-ml-pipeline` as a sibling of evaluate).
- Treat smoke as a **step of build** that runs
  `python -m skore_skills smoke run --stem <stem>`.
- Name the post-smoke AskUserQuestion (Evaluate (Recommended) /
  Modify / Stop) before full-dataset evaluation.
- Preserve the matching experiment stem.
- Name `python -m skore_skills git end-turn --stage implement`
  after the implement loop (after HITL, evaluate, audit, and
  record-outcome — not before the Evaluate pick).
- If that command returns `invoke`, load `persist-ml-git`.

**Must NOT do:**
- Duplicate detailed build / smoke / evaluate / audit previews
  from the dispatcher.
- Load `smoke-test-ml-pipeline` as a sibling dispatcher step.
- Write `skore.evaluate` or load `evaluate-ml-pipeline` /
  `audit-ml-pipeline` before the Evaluate HITL pick.
- Replace skrub DataOps with a bare sklearn Pipeline.
- Mark the experiment done while smoke tests fail.
- Run `git commit` in this skill or `git push`.
- Distill `scratch/research/` here instead of loading
  `build-ml-pipeline`.
- Run `python -m skore_skills model choices` for this explicit,
  already-approved stem.

---

## CASE_02 — Missing design note stops before code

**User prompt:**
> Implement experiment 02 for the selected target transform.

**Assumed workspace state:**
- The Backlog choice is confirmed with stem `02_target_transform`.
- `journal/02_target_transform.md` does not exist.

**Must do:**
- Name `python -m skore_skills scaffold --journal --stem
  02_target_transform` to create the packaged design-note shell.
- State that Question, Motivation, Method, and Risks are filled only
  after that command creates the shell, then stop for user approval.

**Must NOT do:**
- Write model or experiment code before the design note is approved.
- Recreate or fill the design-note shape from memory when the CLI
  command did not run this turn.

---

## CASE_03 — Site on rebuilds after implement

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.
- `policy.site` is true. `policy.notebooks` is false.
- `export-ml-site` is installed.

**Must do:**
- Dispatch `build-ml-pipeline` (`smoke run` inside build).
- Name the post-smoke HITL before evaluate.
- Name `python -m skore_skills site build` after the unfitted
  `pipeline.html` snapshot (before Evaluate is fine) so Method
  shows the diagram, and again after the implement loop before
  git end-turn.
- Name `python -m skore_skills git end-turn --stage implement`.

**Must NOT do:**
- Fail the model turn if site build errors; name the error.
- Run `notebook convert` while the notebooks gate is off.
- Run `git commit` in this skill or `git push`.
- Write `skore.evaluate` before the Evaluate HITL pick.

---

## CASE_04 — Notebooks on converts the experiment script

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Approved design note and experiment shell exist with stem
  `01_baseline`.
- `policy.notebooks` is true. `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.
- `jupytext`, `nbclient`, and `nbconvert` are installed.

**Must do:**
- Dispatch `build-ml-pipeline` (`smoke run` inside build).
- Name `python -m skore_skills notebook convert
  experiments/01_baseline.py --html` after the implement loop,
  before site build.
- Name `python -m skore_skills site build` before git end-turn.
- Name `python -m skore_skills git end-turn --stage implement`.

**Must NOT do:**
- Fail the model turn if convert errors; name the error.
- Run `cells run` as a substitute for convert.
- Run `git commit` in this skill or `git push`.
- Write `skore.evaluate` before the Evaluate HITL pick.

---

## CASE_05 — Smoke red or Stop does not start evaluate

**User prompt:**
> The baseline design is approved. Implement the model. Pytest
> smoke is red on row count.

**Assumed workspace state:**
- Approved design and experiment script exist.
- `tests/smoke/test_01_baseline.py` fails pytest (row count).

**Must do:**
- Stay with `build-ml-pipeline` / `smoke run` to fix topology.
- Name that JSON `stop` keeps the loop in build.

**Must NOT do:**
- Load `evaluate-ml-pipeline` or write `skore.evaluate`.
- Load `audit-ml-pipeline`.
- Loosen the smoke assertion so pytest passes.

---

## CASE_06 — First-model menu without EDA or Backlog

**User prompt:**
> Let us start modeling. What can we do?

**Assumed workspace state:**
- Scaffolded workspace.
- No experiment scripts or completed/running History rows.
- `status.data_analysis` is `missing`.
- Backlog is empty.

**Must do:**
- Name `python -m skore_skills status` and
  `python -m skore_skills model choices`.
- Ask one question with, in order: Build a dummy predictor;
  Build a standard baseline; Discuss the next step.

**Must NOT do:**
- Offer an EDA-derived proposal.
- Offer Pick from the Backlog.
- Write model code before a proposal and design are approved.

---

## CASE_07 — Existing model with EDA and Backlog

**User prompt:**
> Start the next modeling iteration.

**Assumed workspace state:**
- `experiments/01_baseline.py` exists.
- `status.data_analysis` is `present`.
- Backlog contains B1 and B2.

**Must do:**
- Name `python -m skore_skills model choices`.
- Ask one question with, in order: Propose a pipeline from the
  EDA; Pick from the Backlog; Discuss the next step.

**Must NOT do:**
- Offer a dummy predictor or standard baseline.
- Silently pick B1.

---

## CASE_08 — Skipped EDA is not an EDA proposal

**User prompt:**
> What model should we build next?

**Assumed workspace state:**
- A prior experiment exists.
- `status.data_analysis` is `skipped`.
- Backlog is empty.

**Must do:**
- Offer only Discuss the next step.

**Must NOT do:**
- Treat skipped EDA as recorded findings.
- Offer dummy, standard baseline, EDA proposal, or Backlog.

---

## CASE_09 — Discussion becomes a confirmed proposal

**User prompt:**
> I want to talk through what to model next.

**Assumed workspace state:**
- The user selected Discuss the next step.

**Must do:**
- Preview this route as LLM discussion over recorded project
  facts, with no model fit, smoke test, or CV before confirmation.
- Discuss what to learn, why now, and what changes.
- Once an idea is agreed, restate it and wait for an explicit yes
  before creating a design note.

**Must NOT do:**
- Claim local model computation is running during the discussion.
- Force a free-text / artifact entry menu.
- Emit a proposal or model code before confirmation.
- Create the design note before that explicit yes.

---

## CASE_10 — Backlog selection consumes one real row

**User prompt:**
> Pick from the backlog.

**Assumed workspace state:**
- CLI returned B1 and B3; B2 was previously consumed.

**Must do:**
- Load `manage-ml-backlog` and present B1 and B3 in that order.
- Ask for one selection and preserve the unselected row.

**Must NOT do:**
- Renumber B3 to B2.
- Invent a new Backlog item.

---

## CASE_11 — Implement loop gates review before record-outcome

**User prompt:**
> Evaluate it.

**Assumed workspace state:**
- `01_baseline` design note approved; smoke green.
- The user chose Evaluate at the post-smoke gate.
- `evaluate-ml-pipeline` and `review-ml-experiment` are installed.
- `review consent` returns `ask`.
- `policy.notebooks` and `policy.site` are both true.

**Must do:**
- Run evaluate, then `review consent`.
- On `ask`, let `review-ml-experiment` preview the audit cost and
  ask Review / Skip / Stop. Do not load `audit-ml-pipeline` from
  this dispatcher.
- After Review, load `manage-ml-backlog` in record-outcome mode
  with the returned digest, locator, and G-AUDIT-FINDING.
- Record before `notebook convert` and `site build`.
- Write 2–6 sentences from the digest, link `journal/01_baseline.md`,
  name `<package>.html` and `html/01_baseline.html`, and include
  locator plus G-AUDIT-FINDING in the user-facing close.
- Name `python -m skore_skills git end-turn --stage implement`
  last.

**Must NOT do:**
- Run `cells run` from this dispatcher before Review.
- Leave History `planned` in any journal excerpt you author.
- Convert `audit/01_baseline.py` here — the audit skill did it.
- Open idea triage inside record-outcome mode.
- Write the journal files directly instead of dispatching.

---

## CASE_12 — Skip review still records the locator

**User prompt:**
> Finish the successful baseline evaluation.

**Assumed workspace state:**
- Smoke is green and evaluate returned
  `[Open report](https://example.invalid/report/42) · hub · id: 42`.
- The user answered Skip at the review gate.

**Must do:**
- Pass the exact locator to `manage-ml-backlog` record-outcome.
- Pass G-AUDIT-FINDING `n/a — audit not run`.
- Write 2–6 sentences of the result and link `journal/<stem>.md`.
- Include the same locator in the user-facing close (first among
  tokens).
- Record before convert, site build, and git end-turn.

**Must NOT do:**
- Run the skore-check audit after Skip.
- Write `journal/ideas/` files.
- Drop the locator because there is no audit digest.
- Invent a headline metric.
- Open idea triage.

---

## CASE_13 — Planned design note uses one approval gate

**User prompt:**
> The design note is written. Approve it and implement.

**Assumed workspace state:**
- `journal/02_target_transform.md` exists with State `planned`.
- Question, Motivation, Method, and Risks are filled.
- `design consent` returns `ask` with choices approve, modify, stop.

**Must do:**
- Ask one AskUserQuestion, in order: Approve / Modify / Stop.
- On Approve, set State to `approved` and Approved by user on to
  a `YYYY-MM-DD` date, then require `design consent` `proceed`
  before code.

**Must NOT do:**
- Also ask in chat whether the note looks right.
- Treat "Approve it and implement" as approval before the gate.
- Write model code while State is still `planned`.

---

## CASE_14 — Skipped EDA still site-builds before Evaluate

**User prompt:**
> The baseline design is approved. Implement and test the model.

**Assumed workspace state:**
- Matching approved design note and experiment shell exist.
- `status.data_analysis` is `skipped`. No
  `data_analysis/data_analysis.md`.
- `policy.site` is true. `export-ml-site` is installed.
- `build-ml-pipeline` is installed.

**Must do:**
- Dispatch `build-ml-pipeline`.
- Require `python -m skore_skills site build` after the unfitted
  `pipeline.html` snapshot and before the Evaluate question,
  inside that build.
- Keep the post-loop `site build` for the fitted diagram.

**Must NOT do:**
- Defer the first `site build` until after `skore.evaluate`.
- Skip the pre-Evaluate site build because EDA was skipped.
