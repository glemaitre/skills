---
name: explore-ml-directions
description: >
  Optional router for the next experiment idea. Ask which installed
  source to use (user idea, literature, last audit, backlog row),
  then ask Draft, Park, or Stop. Trigger on "what should we try",
  "explore ideas", or when triage recommends the backlog stage.
  Do not record outcomes, write journal files, or design the
  experiment.
---

# Explore ML Directions

Route only. Do not search, shape an idea, mine a digest, or write
`journal/`.

## Procedure

1. Run `python -m skore_skills status`. Read `status.skills`.
   When offering a Backlog row, also run
   `python -m skore_skills model choices` and read `backlog`.
2. **AskUserQuestion** with the installed sources only. One pick:

   | Label | Load when |
   |---|---|
   | I have an idea or a specific source | `status.skills.iterate-from-user` |
   | Look up the literature | `status.skills.iterate-from-literature` |
   | Mine the last audit | `status.skills.iterate-from-skore` |
   | Use a Backlog row | `status.skills.manage-ml-backlog` and `backlog` is non-empty |

   Omit a row that fails its check. Pass the `backlog` array into
   `manage-ml-backlog` model-entry selection mode. Do not add a
   Backlog idea here. If no row qualifies, say so in one line and
   load `triage-ml-task` when `status.skills.triage-ml-task` is
   true. Do not invent a child's steps.

3. When the child returns a confirmed Proposal or Backlog
   candidate rows, **AskUserQuestion** once:

   - **Draft** — load `model-ml-pipeline` only if
     `status.skills.model-ml-pipeline` is true and hand it the
     Proposal. That skill owns the design note. Missing skill →
     one-line skip; leave the Proposal in chat.
   - **Park** — if the caller is already `manage-ml-backlog`,
     return the rows to that caller. Otherwise load
     `manage-ml-backlog` only if that id is true so it appends
     stable `B<N>` rows and does not reopen this menu. Missing
     skill → one-line skip; leave the rows in chat.
   - **Stop** — load `triage-ml-task` only if that id is true.

4. A return with no Proposal and no candidate rows re-shows the
   source menu in step 2. Do not ask Draft / Park / Stop.

## Stop conditions

- Do not write `journal/` or a design note.
- Do not pick a direction, a Backlog row, or a winner for the user.
- Do not search the web, read an audit digest, or shape a Proposal
  in this skill.
- Do not run record-outcome, `git end-turn`, or `site build`.
- Do not invent a missing child's procedure.
