---
name: model-ml-pipeline
description: >
  Deterministic entry point for modeling. On a generic landing,
  offer only the choices justified by the workspace (first-model
  dummy / standard baseline, EDA proposal, Backlog, discussion).
  After a design is approved, coordinate build (pytest smoke is a
  build sub-step), the user's Evaluate (Recommended) / Modify /
  Stop gate, evaluation, and audit. Not for a single action
  already owned by evaluate, audit, or smoke debugging.
---

# Model ML Pipeline

This meta skill owns selection and ordering, not child methodology.
Do not load `smoke-test-ml-pipeline` as a sibling of evaluate.

## Entry routing — deterministic

1. Run `python -m skore_skills status`. If `has_src` and
   `has_journal` are both false, STOP: explain and send the user
   to `setup-ml-project` / triage. Do not require `git`.
2. **Resume beats menu.** If the user names an experiment stem, or
   `status.policy.loop.stem` / `last_history_stem` identifies a
   current design, run
   `python -m skore_skills design consent --stem <stem>`. Treat
   JSON `action` as authoritative. `proceed` → resume that stem
   directly; do not ask how to start again. `ask` → show the note
   and **stop** for approval; do not write code. `stop` → missing
   note: name `scaffold --journal --stem` (or abandoned: explain
   and do not implement). Do not infer approval from "build it".
3. Otherwise run `python -m skore_skills model choices`. Treat its
   JSON as authoritative. Present exactly `choices[]`, in returned
   order, in one single-choice **AskUserQuestion**:
   - `dummy` → **Build a dummy predictor**
   - `standard_baseline` → **Build a standard baseline**
   - `eda_proposal` → **Propose a pipeline from the EDA**
   - `backlog` → **Pick from the Backlog**
   - `discuss` → **Discuss the next step**

Do not add a disabled choice, infer availability yourself, or
reorder the list. In particular: no dummy / standard baseline when
`model_stems` is non-empty; no EDA proposal unless
`data_analysis` is `present`; no Backlog option when `backlog` is
empty. Discussion is always present.

## Choice contracts

Every choice first produces a user-confirmed proposal and an
approved design note. No branch writes model code before approval.
Use the next available numeric stem; never overwrite an existing
note.

- **Dummy predictor (`dummy`).** Determine classification vs
  regression from recorded project facts; ask if unknown. Propose
  `DummyClassifier` or `DummyRegressor` inside the normal skrub
  DataOps declaration. Its purpose is structural: prove loading,
  fit/predict, and pytest smoke work; it is not expected to add
  predictive value. Keep the normal post-smoke Evaluate
  (Recommended) / Modify / Stop gate.
- **Standard baseline (`standard_baseline`).** Propose a quick
  traditional-ML baseline: skrub automatic preprocessing plus a
  task-appropriate standard estimator, with no domain feature
  engineering. It establishes a real comparison point. Confirm the
  proposal and design before build.
- **EDA proposal (`eda_proposal`).** Read
  `data_analysis/data_analysis.md` and the project goal. Cite the
  EDA findings that motivate one pipeline proposal. Do not invent
  findings or present multiple silent alternatives. Confirm the
  proposal and design before build.
- **Backlog (`backlog`).** Load `manage-ml-backlog`. Pass the
  `backlog` rows returned by the CLI; ask the user to pick one
  `B<N>`, consume only that row into a proposal/design stem, then
  return here. Do not add a new Backlog idea in this branch.
- **Discussion (`discuss`).** Have an open conversation about what
  to learn, why now, and what changes. Once an idea is agreed,
  summarize it as a Proposal using `iterate-from-user`'s three
  shaping questions and confirmation contract, but do not force
  its article/resource/free-text entry menu. Only after explicit
  confirmation create/populate the design note and seek approval.
  If no idea is agreed, return to the entry choices.

If the design-note shell is missing, this turn only names
`python -m skore_skills scaffold --journal --stem <NN_short>`
and stops. Do not fill Question / Motivation / Method / Risks
from memory. Populate those sections only after that command
has created the shell, then stop for explicit design approval.

## Approved-design implement loop

1. `build-ml-pipeline` — declare the skrub DataOps learner. That
   skill loads `smoke-test-ml-pipeline` after the experiment file
   exists and **runs pytest** on `tests/smoke/test_NN_*.py`. Red
   pytest stays in build (modify the pipeline, re-run pytest).
   Green pytest: build reports the design, then
   `python -m skore_skills evaluate consent --stem <stem>`
   (Evaluate / Modify / Stop on `ask`).
2. Only if the user chose **Evaluate** and smoke is green:
   `evaluate-ml-pipeline` — leakage-safe splitter and
   `skore.evaluate` in the experiment script. Re-run `status`
   first, then `python -m skore_skills evaluate consent --stem
   <stem>`. Consent JSON is authoritative, not the user's wording
   alone. Missing `evaluate-ml-pipeline` → one-line skip.
3. After a successful evaluate: `audit-ml-pipeline` if installed
   (same stem). Missing skill → one-line skip. Re-run `status`
   first. No report → do not invent an audit; stop.
4. After audit — or after evaluate when audit was skipped — load
   `manage-ml-backlog` in **record-outcome mode**, handing it the
   normalized G-REPORT-LOCATOR and the optional audit digest or
   headline. It writes the `JOURNAL.md` History row and design-note
   Status block, then returns; it does not rescan the Backlog or
   open the next-lever menu. Never mark `done` while smoke is red.
   Audit-skipped runs still record the locator; missing headline
   becomes `n/a`, never an invented metric. The Evaluate
   branch's visible close is that dispatch sequence. Do not claim
   History remains `planned` because a child was not executed
   in-process.

Do not duplicate child-skill methodology. Before new library
symbols are written, children use
`python -m skore_skills api get <dotted>`.

## Stop conditions

- Unscaffolded workspace (`has_src` and `has_journal` both
  false): setup/triage; do not start build.
- Generic model landing: do not hand-author the menu; run
  `python -m skore_skills model choices`.
- If `journal/NN_<short>.md` is missing, this turn only names
  `python -m skore_skills scaffold --journal --stem
  <NN_short>` and stops. Do not recreate or fill the template
  from memory. Populate Question / Motivation / Method / Risks
  only after that command has created the shell, then stop for
  user approval.
- Require `design consent` `proceed` before code. Do not treat
  "the user asked to build" as approval.
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while smoke tests fail.
- Do not load evaluate (or write `skore.evaluate`) before the
  post-smoke HITL answer is Evaluate (`evaluate consent` `ask`),
  except `proceed` for a stem that already has a persisted report,
  or while pytest is red.
- Do not load `smoke-test-ml-pipeline` from this dispatcher.
- Do not duplicate child-skill methodology in this dispatcher.
- If `status.data_analysis` is `missing`, continue with facts the user
  stated; do not invent an exploratory data analysis report.
- Literature-backed feature-engineering or learner-family
  questions: load `build-ml-pipeline` (it loads
  `research-ml-practice` if installed). Do not distill research
  here; do not invent papers from memory.

After **Stop**, or while smoke is red: skip evaluate, audit, and
record-outcome. This is an explicit no-result close: do not mark
the experiment done, but still perform the conversion/site steps
below when applicable, then run `git end-turn` and return to triage.
If `policy.notebooks` is true and `export-ml-notebook` is
installed, run
`python -m skore_skills notebook convert experiments/<stem>.py`
only when the experiment script already exists, with `--html`
when `policy.site` is also true. Convert re-executes the
script; say so when it is slow. Missing jupytext / nbclient /
nbconvert → one-line skip naming `add-python-package`; do not
fail the turn.

After **Evaluate** (and audit if it ran), implement-loop step 4
(record-outcome) runs first, so the journal files are on disk
before anything is staged. The user-facing close **must** include
the G-REPORT-LOCATOR value evaluate passed up (or
`n/a — backend did not expose a locator`). Then the same
convert/site rules apply. `audit-ml-pipeline` converts `audit/<stem>.py` itself; do
not convert it again here. The site appends that viewer to the
experiment page as the continuation of evaluate.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build`. Skip in one line otherwise.
Name a build error; do not fail the model turn.

Then run
`python -m skore_skills git end-turn --stage implement`. If JSON
`action` is `invoke`, load `persist-ml-git` and stop; that skill
returns to triage. Otherwise load `triage-ml-task`. Do not run
`git commit` in this skill.
Never mark `done` while smoke is red.
