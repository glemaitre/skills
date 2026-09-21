---
name: manage-ml-backlog
description: >
  Canonical backlog loop step. Record an experiment outcome in
  History, refresh Backlog, and name next-lever options. Also
  supports the model-entry selection mode: show real B<N> rows
  supplied by the deterministic CLI and consume one into a
  proposal. Trigger after audit, when a run finishes, when the
  user asks what to try next, or when model-ml-pipeline routes its
  Backlog choice here. This is cadence, not a methodology owner.
---

# Manage ML Backlog

Replace iterate-as-cadence. Do not own setup, exploratory data
analysis, build, smoke,
evaluate, or audit methodology.

## Model-entry selection mode

When `model-ml-pipeline` calls with the `backlog` array from
`python -m skore_skills model choices`:

1. Present exactly those `B<N>` rows in their returned order and
   AskUserQuestion for one pick. Do not rescan into a different
   menu and do not add an idea.
2. Turn the selected row's Item + Source into a Proposal. Ask only
   for missing shaping facts; do not invent a Method from a
   one-line item.
3. Return the confirmed Proposal to `model-ml-pipeline`. After the
   model stage creates and populates the design note, remove only
   the selected Backlog row and add the planned History row.
   Preserve every other stable B<N> index.

This mode does not require a report/audit digest and does not run
the outcome-recording procedure below. Empty Backlog is a routing
error: return to `model-ml-pipeline`; do not fabricate B1.

## Record-outcome mode

When `model-ml-pipeline`, `evaluate-ml-pipeline`, or
`audit-ml-pipeline` calls at end of turn with the normalized
G-REPORT-LOCATOR plus an optional audit digest or user-supplied
headline. This is the only path that records an outcome without a
full backlog turn. Audit may have been skipped; the locator remains
required.

Run Procedure steps 1-3 and nothing else:

1. Step 1 — `python -m skore_skills status`; require an approved
   stem.
2. Step 2 — read `journal/JOURNAL.md`; scaffold the index if it is
   missing.
3. Step 3 — update the matching History row and design-note Status
   block from the digest or user-supplied headline when available,
   including the digest locator pasted verbatim. Also refresh
   the `JOURNAL.md` Status rows `Last experiment` and `Last result`.

Then return to the caller. Skip step 4 (Backlog rescan) and step 5
(the next-lever triage menu) — the caller did not ask what to try
next.

Do not dispatch `audit-ml-pipeline` in this mode; the digest is
already in hand and dispatching would bounce back here. Do not run
this skill's End of turn either: the caller owns convert / site /
`git end-turn`.

The Procedure guards still bind. Never mark `done` while smoke is
red, and never invent a metric — no digest and no user-supplied
value means use `n/a`, not a guess. Never construct a missing
backend URL. Record `n/a — backend did not expose a locator` in
both markdown destinations when the digest has no authoritative
locator.

## Procedure

1. Run `python -m skore_skills status`. When recording a done
   outcome, run
   `python -m skore_skills design consent --stem <stem>`.
   `ask` / `stop` → do not mark `done`. Also require green smoke
   evidence and a normalized report locator. An audit digest is
   optional.
2. Read `journal/JOURNAL.md` History and Backlog. If the index is
   missing, run `python -m skore_skills scaffold --journal`. Do
   not write or paste the file. The CLI writes four sections:
   Status, Data understanding, History, and Backlog. If that
   command cannot run this turn, name it and stop. After the file
   exists, edit the existing History and Backlog tables (columns:
   Stem, Intent, Status, Headline result, Report, Design note; and
   #, Item, Source). A planned History row uses `n/a` in Report.
   Stable `B<N>` indices. Do not renumber on removal.
3. If recording a run: copy the headline metric from the audit
   digest or the user's value. Do not invent numbers. Update the
   matching History row (`planned` → `done` only if smoke passed).
   Copy the digest's persisted-report locator into the History
   `Report` cell and the design note's `Persisted report` Status
   line. Paste that string verbatim; do not paraphrase it as
   "normalized" or rewrite the Hub URL. If
   the digest has none, write
   `n/a — backend did not expose a locator` in both places; do not
   derive or guess a URL. Update the rest of the design-note Status
   block the same way.
4. Perform a full Backlog rescan. Resolve rows the run answered or
   killed, preserving stable indices. Then route sourcing explicitly:
   report-derived ideas → `iterate-from-skore`; user proposals →
   `iterate-from-user`; an existing row or stop → `model-ml-pipeline`.
   Returned candidates/proposals are written by this parent, not by
   either sourcing child.
5. Ask whether to draft from the refreshed Backlog or stop. When a
   row is selected, return it to `model-ml-pipeline`, which can
   create its design-note shell with
   `python -m skore_skills scaffold --journal --stem <NN_short_name>`.
   Do not draft that template in this backlog turn.

## Stop conditions

- Do not design or implement the next experiment in this turn.
- Do not dispatch setup, model, or audit by skill id.
- In model-entry selection mode, do not invent a Backlog row or
  remove it before the paired design note exists.
- Do not invent metrics.
- Do not paste a `JOURNAL.md` body or recreate the index from
  memory.
- Do not mark `done` while smoke is red.
- Design approval is owned by `model-ml-pipeline`; this skill only
  returns a confirmed proposal or selected Backlog row.

## End of turn

If `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build`. Do not run
`notebook convert`. Skip
in one line otherwise. Name a build error; do not fail the
backlog turn.

Run `python -m skore_skills git end-turn --stage backlog`. If JSON
`action` is `invoke`, load `persist-ml-git` and stop; that skill
returns to triage. Otherwise load `triage-ml-task`. Do not run
`git commit` in this skill.
