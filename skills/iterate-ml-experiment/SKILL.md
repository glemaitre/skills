---
name: iterate-ml-experiment
description: >
  Own the experiment journal, design approval, sourcing choice,
  cadence, and dispatch to focused workflow skills. Trigger when an
  ML workspace session starts, the user asks for a baseline or next
  experiment, a run finishes, or past experiments must be compared.
  This is a meta skill: it does not inline setup, pipeline, evaluation,
  smoke-test, API, or audit implementation.
---

# Iterate ML Experiment

Keep the user in control of experiment design and cadence.
`journal/JOURNAL.md` is the session index and source of continuity.

## Stop conditions

- **G-DESIGN:** never touch `experiments/NN_*.py` or `src/<pkg>/`
  until matching `journal/NN_<short>.md` exists and is approved.
  “Quick”, “standard”, and “skip questions” do not waive this gate.
- Do not silently choose a sourcing strategy or next experiment.
- Do not inline child methodology. Dispatch setup, model, audit,
  and sourcing skills.
- Do not edit a completed experiment script while recording its
  outcome.
- Do not invent metrics. Copy the user's value or audit digest.
- All smoke tests must pass before a History row becomes `done`.
- Record outcome and propose the next experiment are separate
  cadence decisions.

## Session pre-flight

```
- [ ] Read journal/JOURNAL.md (or identify one-line placeholder)
- [ ] Mode: bootstrap | propose | implement | record | compare
- [ ] Setup status: ready | dispatch setup-ml-project
- [ ] Design status: missing | planned | approved | done
- [ ] Dispatch target named
```

## Mode 0 — bootstrap

No History rows means bootstrap.

1. Read `data/README.md` and propose the project goal default.
2. Dispatch `setup-ml-project` for unresolved G-PKG-NAME,
   G-ENV-MGR, G-TABULAR, and skore-mode setup. Do not duplicate its
   tables.
3. Ensure EDA is recorded; dispatch the `eda` pack when needed.
4. Auto-draft `journal/01_baseline.md` from
   `templates/experiment_design.md`.
5. Ask for G-DESIGN approval. Do not write baseline code yet.

Bootstrap does **not** show the four-option sourcing menu: the first
experiment is the baseline.

## Mode 1 — propose next

With at least one History row, read and surface Backlog, then ask:

1. `skore` — dispatch `iterate-from-skore`
2. `user` — dispatch `iterate-from-user`
3. `my-pick` — offer 2–4 grounded candidates and ask
4. `B<N>` — promote that Backlog row directly

Never silently default to skore because a report exists. After a
source returns a Proposal, draft `journal/NN_<short>.md` and ask for
G-DESIGN approval.

### Free-text resolution

A concrete user idea, article URL, GitHub issue URL, or
`org/repo#N` resolves the source to `iterate-from-user`; pass the
resource link pre-resolved. Do not re-show the menu or ask the user
to paste the issue. Draft only after the sibling returns a Proposal.

## Mode 2 — implement approved design

Dispatch `model-ml-pipeline`. It owns the order:

1. build
2. evaluate
3. smoke-test

Do not jump directly into `evaluate.py`, hard-code a remembered
splitter, or copy the child skills into this file. Before new
library calls, the child runs `python -m skore_skills api get`.

After implementation, ask:

- **run now** — execute the experiment, then continue to record;
- **leave for later** — show Status + Backlog and stop.

## Mode 3 — record outcome

1. Dispatch `audit-ml-pipeline`; execute its file with:

   ```bash
   python -m skore_skills cells run \
     audit/NN_<short>.py scratch/audit/NN_<short>/audit.md
   ```

2. Read the audit digest and `journal/JOURNAL.md`.
3. Confirm **all** `tests/smoke/` pass.
4. Update the design-note Status block:
   - State: `done`
   - Approved by user on: unchanged
   - Headline result: copied verbatim
   - Implication for next iteration: 1–2 grounded sentences
5. Update the matching History row.
6. Scan Backlog and resolve items answered or killed by the run.
7. Ask:
   - **draft the next experiment now**
   - **not yet**

Do not draft `NN+1` in the record-outcome turn before that answer.

## Mode 4 — compare

Read-only pairwise comparison:

1. Read the requested History rows from `JOURNAL.md`.
2. Put their Headline results side by side.
3. Do not write journal files, create a design note, or invoke a
   multi-key ComparisonReport.

## Journal contract

`JOURNAL.md` has only:

1. Status
2. Data understanding (EDA)
3. History
4. Backlog

Per-experiment notes use `templates/experiment_design.md`:
Question, Motivation, Method, Risks, and Status block. No Success
criteria section.

Pairing is hard:

```text
journal/NN_<short>.md
experiments/NN_<short>.py
tests/smoke/test_NN_<short>.py
audit/NN_<short>.py
```

## Dispatch map

- setup → `setup-ml-project`
- data understanding → `explore-ml-data`
- implementation → `model-ml-pipeline`
- report narrative → `audit-ml-pipeline`
- skore diagnostics → `iterate-from-skore`
- user/resource idea → `iterate-from-user`

## References (load on demand)

- `references/bootstrap.md`
- `references/record_outcome.md`
- `references/maintenance_modes.md`
- `references/preflight_evidence.md`
