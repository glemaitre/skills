---
name: iterate-from-literature
description: >
  Turn a user query into a few experiment directions by searching
  scientific and technical sources. Rewrite the query as a problem
  class, fetch primary pages, and let the user pick. Confirm before
  returning a Proposal. Trigger when the user asks what the
  literature says, or when iterate-from-user has a topic and no
  artifact. Do not call research-ml-practice. Do not write journal
  files or pick a winner.
---

# Iterate from literature

Source: a query, not an artifact the user already named. Output: two
to four directions in chat, then — only after the user picks one and
confirms — a Proposal handed back to the caller. This skill does not
load `research-ml-practice`.

## Procedure

1. Run `python -m skore_skills status`. Read `JOURNAL.md` Status
   (goal, task), the last History headline, and the EDA summary in
   `data_analysis/data_analysis.md` when that file exists. If the
   query is missing or too vague to search, ask once for it.
2. **Rewrite the query as a problem class** before any search.
   Drop dataset names, loader names (`sklearn.datasets`,
   `fetch_*`), and Kaggle slugs. JOURNAL and EDA are context for
   that rewrite, not search strings.
3. Search scientific and technical sources (papers, library docs,
   established technical write-ups). Fetch the primary pages.
   When sources disagree, say so. Do not fill a gap from memory
   after a search has run. Do not ask the user to go look it up.
4. Write `scratch/research/direction-<slug>.md` (gitignored). If
   the write cannot run, name that path and continue from what
   was fetched. If search itself cannot run, say so and stop. Do
   not invent papers, URLs, or claims.
5. Show **two to four** directions in chat. Each one has: a
   one-line idea, why it might transfer here, what it would change
   versus the last experiment, and the URL plus the claim. Do not
   paste the scratch note. Do not rank a winner, and do not close
   with "highest-leverage" or "run X next".
6. **AskUserQuestion**: pick one direction, narrow the query, or
   stop. Narrow restarts from step 2. Stop returns to the caller
   with no Proposal.
7. The picked direction uses the confirmation restatement below,
   then the Proposal. Transfer risks and domain claims this dataset
   does not establish stay in `Open gaps`.

## Confirm before returning

> "From <url>, I understand you'd like to **<one-line intent>** —
> concretely, change `src/<pkg>/<file>.py` to
> **<method-outline-summary>**. Open gaps: **<bullets>**. Does this
> capture what you want before I hand it back?"

Until the user says yes, that paragraph is the whole message. Do
not emit a `Proposal (` header before yes. "Not yet" or "stop"
returns with no Proposal.

## What is returned

```
Proposal (from: literature):
  Question:        <one sentence>
  Motivation:      <why now, tied to the fetched claim>
  Source:          <url — "exact claim">
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Open gaps:       <transfer risks, disagreements, domain assertions>
```

No `Success` field. No `journal/` write. No package install. Do not
pick the learner.

## Stop conditions

- Do not search the dataset proper name, a loader, or a Kaggle slug.
- Do not load `research-ml-practice` or paste its scratch note.
- Do not write `journal/` or a design note.
- Do not add a package or run `env add` / `pixi add`.
- Do not treat one blog as ground truth.
- A new library named only by a source stays in `Open gaps` until
  the user asks to add it. Then name it in `Method outline` and
  load `add-python-package` when that skill is installed.

## Companion skills

- **`explore-ml-directions`** — usual caller; owns Draft / Park /
  Stop.
- **`iterate-from-user`** — the user already has an idea or an
  artifact.
- **`research-ml-practice`** — in-stage EDA and build worker. Not
  called from here.
