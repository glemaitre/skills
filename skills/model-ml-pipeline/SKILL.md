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
   directly; do not ask how to start again. `ask` → Design approval
   below; do not write code. `stop` → missing
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
approved design note. The proposal yes agrees the idea. The note
is approved only by Design approval below. No branch writes model
code before that gate is `proceed`. Use the next available numeric
stem; never overwrite an existing note.

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
  proposal, write the note, then Design approval, before build.
- **EDA proposal (`eda_proposal`).** Read
  `data_analysis/data_analysis.md` and the project goal. Cite the
  EDA findings that motivate one pipeline proposal. Do not invent
  findings or present multiple silent alternatives. Confirm the
  proposal, write the note, then Design approval, before build.
- **Backlog (`backlog`).** Load `manage-ml-backlog` only if
  `status.skills.manage-ml-backlog` is true. Else one-line skip;
  do not invent a Backlog. Pass the
  `backlog` rows returned by the CLI; ask the user to pick one
  `B<N>`, consume only that row into a proposal/design stem, then
  return here. Do not add a new Backlog idea in this branch.
- **Discussion (`discuss`).** Have an open conversation about what
  to learn, why now, and what changes. Restate the agreed idea and
  wait for an explicit yes before any design note. Only after that
  confirmation create/populate the design note, then Design
  approval. If no idea is agreed, return to the entry choices.

## Before execution

This dispatcher labels the next kind of work but does not
duplicate a child's detailed preview.

- For `discuss`, proposal shaping, or literature-backed design
  work, emit 1–3 natural sentences saying this is **LLM
  discussion/research** over recorded project facts, with no
  model fit, smoke test, or CV. Name any scratch research note or
  design note that may be written and stop at confirmation.
- For an approved implementation, say which child comes next and
  the broad sequence: local pipeline preparation → small
  real-data smoke fit/predict → optional full-dataset evaluation
  → gated review. Then let `build-ml-pipeline`,
  `smoke-test-ml-pipeline`, `evaluate-ml-pipeline`, and
  `review-ml-experiment` each own the single detailed Before
  execution preview at its actual compute boundary.

Do not invent minute estimates at dispatcher level. Name a known
duration only when explicit measured evidence is available;
otherwise leave cost details to the child that knows data scope,
folds, and selected views. Pending proposal/design approval may
preview the sequence but never starts local work.

If the design-note shell is missing, this turn only names
`python -m skore_skills scaffold --journal --stem <NN_short>`
and stops. Do not fill Question / Motivation / Method / Risks
from memory. Populate those sections only after that command
has created the shell, then Design approval.

## Design approval

One gate approves a populated note. Run
`python -m skore_skills design consent --stem <stem>`.
`proceed` → already approved; do not ask again. `ask` → show the
note and **AskUserQuestion** (single choice), in order:
**Approve** / **Modify** / **Stop**. Do not also ask in chat
whether the note looks right.
- **Approve** → set `**State:**` to `approved` and
  `**Approved by user on:**` to today's date (`YYYY-MM-DD`).
  Re-run `design consent`; code starts only on `proceed`.
- **Modify** → leave `State` `planned`, edit the note, and ask
  this gate again.
- **Stop** → do not implement.

## Approved-design implement loop

1. Load `build-ml-pipeline` only if `status.skills.build-ml-pipeline`
   is true; else one-line skip and stop — do not declare the
   pipeline from this meta. That skill loads `smoke-test-ml-pipeline`
   after the experiment file exists and runs
   `python -m skore_skills smoke run --stem <stem>`. JSON `stop`
   stays in build (modify the pipeline, re-run `smoke run`).
   `proceed`: build reports the
   design, then
   `python -m skore_skills evaluate consent --stem <stem>`
   (Evaluate / Modify / Stop on `ask`). Build also writes the
   unfitted `scratch/results/<stem>/pipeline.html` and, when
   `policy.site` is true, runs `site build` so Method shows the
   diagram **before** Evaluate. Do not convert
   `experiments/<stem>.py` at that point if it already contains
   `skore.evaluate`.
2. Only if the user chose **Evaluate** and `smoke run` is `proceed`: load
   `evaluate-ml-pipeline` only if `status.skills.evaluate-ml-pipeline`
   is true — leakage-safe splitter and
   `skore.evaluate` in the experiment script. Re-run `status`
   first, then `python -m skore_skills evaluate consent --stem
   <stem>`. Consent JSON is authoritative, not the user's wording
   alone. Missing `evaluate-ml-pipeline` → one-line skip. Do not
   invent that skill's steps.
3. After a successful dispatched evaluate (locator returned): run
   `python -m skore_skills review consent --stem <stem>`. Treat
   JSON `action` as authoritative.
   - `stop` — no `report.html`. Do not review. Name the missing
     file. Do not record-outcome.
   - `ask` — the review skill owns the cost preview and
     Review (Recommended) / Skip / Stop question. Load
     `review-ml-experiment` only if
     `status.skills.review-ml-experiment` is true so it can ask.
     Missing skill → one-line skip and record-outcome with
     `n/a — audit not run`.
   - **Review** or `proceed` — load `review-ml-experiment` (same
     gate). It returns the digest, G-AUDIT-FINDING, locator, and
     idea paths. Do not load `audit-ml-pipeline` from this
     dispatcher.
   - **Skip** — no idea files. Record-outcome with
     `n/a — audit not run`.
   - **Stop** — do not record-outcome and do not audit. Return
     to triage when `status.skills.triage-ml-task` is true.
4. After **Review** or `proceed`, or after **Skip** / a missing
   review skill: load `manage-ml-backlog` only if
   `status.skills.manage-ml-backlog` is true, in **record-outcome
   mode**, handing it the locator, optional headline, and
   G-AUDIT-FINDING (`n/a — audit not run` when skipped). Else
   one-line skip; do not write History from this meta. It writes
   the `JOURNAL.md` History row and design-note Status block plus
   `## Results`, then returns. It does not triage idea files in
   this mode. Never mark `done` while `smoke run` is `stop`.
   Missing headline becomes `n/a`, never an invented metric. Do
   not claim History remains `planned` because a child was not
   executed in-process.

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
  only after that command has created the shell, then Design
  approval.
- Require `design consent` `proceed` before code. Do not treat
  "the user asked to build", or a chat yes on the drafted note,
  as approval.
- Preserve identical stems across design, experiment, smoke, audit.
- Do not replace skrub DataOps with bare sklearn Pipeline.
- Do not persist a result as done while `smoke run` is `stop`.
- Do not load evaluate (or write `skore.evaluate`) before the
  post-smoke HITL answer is Evaluate (`evaluate consent` `ask`),
  except `proceed` for a stem that already has a persisted report,
  or while `smoke run` is `stop`.
- Do not load `smoke-test-ml-pipeline` from this dispatcher.
- Do not duplicate child-skill methodology in this dispatcher.
- If `status.data_analysis` is `missing`, continue with facts the user
  stated; do not invent an exploratory data analysis report.
- Literature-backed feature-engineering or learner-family
  questions: load `build-ml-pipeline` only if
  `status.skills.build-ml-pipeline` is true (it loads
  `research-ml-practice` only if `status.skills.research-ml-practice`
  is true). Else one-line skip. Do not distill research
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

After **Review** or **Skip** (or a missing review skill),
implement-loop step 4 (record-outcome) runs first, so the journal
files are on disk before anything is staged. **Stop** skips
record-outcome. This dispatcher owns the User-facing close.
Children return locator / digest / finding and do not preview
this close.

### User-facing close

The user-facing message is a short story plus links. It is not
Pre-flight, not a dump of the digest or design note, and not
locator/finding alone.

1. **Narrative first** — 2–6 sentences of the result, grounded in
   the audit digest when present (Checks + Metrics), else the
   user's headline / `report.txt`. Do not invent a metric.
2. **Open these** — markdown links plus the resolved absolute
   path for local files: `[journal/<stem>.md](journal/<stem>.md)`.
   If `policy.site` is true and `site build` ran or is about to:
   `[<package>.html](<workspace>/<package>.html)` and
   `html/<stem>.html`.
3. **Normalized tokens second** — G-REPORT-LOCATOR evaluate
   passed up (or `n/a — backend did not expose a locator`) first
   among tokens, then G-AUDIT-FINDING (`n/a — audit not run`
   when skipped). Index strings, not the narrative.

Then the same convert/site rules apply. `audit-ml-pipeline`
converts `audit/<stem>.py` itself; do not convert it again here.
The site appends that viewer to the experiment design note's
`## Notebooks` section after evaluation.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build` so the fitted Method pipeline
diagram (and Results) replace the construct-time snapshot. Skip in
one line otherwise.
Name a build error; do not fail the model turn. Name
`<package>.html` (and `html/<stem>.html`) in the User-facing
close when the build ran.

Then run
`python -m skore_skills git end-turn --stage implement`. If JSON
`action` is `invoke`, load `persist-ml-git` only if
`status.skills.persist-ml-git` is true and stop; that skill
returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop. Do not run
`git commit` in this skill.
Never mark `done` while smoke is red.
