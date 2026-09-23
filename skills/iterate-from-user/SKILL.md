---
name: iterate-from-user
description: >
  Shape a next-experiment idea the user already has, or answer a
  question about the current project. Two entries: a free-text idea,
  or a concrete artifact (URL, GitHub issue, spec file, reference
  repo). A topic with no source belongs to `iterate-from-literature`.
  Confirm before returning a Proposal. A question-only turn returns
  no Proposal. Hand the result back to the caller. Never writes a
  design note or acceptance criteria.

  TRIGGER when: `explore-ml-directions`, `triage-ml-task`,
  `manage-ml-backlog`, or `model-ml-pipeline` Discuss loads this
  skill; the user volunteers a concrete idea ("I want to try X");
  the user pastes or links an article, GitHub issue, spec file, or
  reference repo.

  SKIP when: the user wants to mine the previous report (use
  `iterate-from-skore`); the user names a topic and no artifact
  (use `iterate-from-literature` when installed); the user is
  asking for a symbol lookup (`python -m skore_skills api get`);
  the work is evaluation mechanics on a new run (route to
  `evaluate-ml-pipeline`); the user wants a narrative read of an
  existing report (route to `audit-ml-pipeline`).

  HOW TO USE: open with an `AskUserQuestion` for free-text vs
  artifact, unless the entry is already resolved. Fetch or read
  the artifact. Answer a project question from workspace facts
  and stop with no Proposal. For an idea, walk the three shaping
  questions and confirm in plain text before returning the
  Proposal.
---

# Iterate from user

Source: the user — an idea, a question, or an artifact they named.
Output: either a short answer with **no Proposal**, or a
**user-confirmed** Proposal block, handed back to the caller
(`explore-ml-directions`, `triage-ml-task`, `manage-ml-backlog`,
or `model-ml-pipeline`).

## Output contract (read this before the body)

This skill **never writes `journal/` files** and **never authors
acceptance criteria**. A Proposal, when one is returned, is
conversation text (full shape in § What is returned):
`Question`, `Motivation` (with `Source` field — quote, URL, or path),
`Method outline`, `Open gaps`. A Proposal requires:

- All three **shaping questions** are answered (see § The three
  shaping questions).
- The **synthesis confirmation gate** has fired and the user has
  said yes (see § Confirm before returning).
- **`Source`** is concrete: the user's quote, the article URL with
  the exact claim, the `gh issue` link, or the spec-file path with
  line numbers.

**No Proposal is a valid outcome.** A project question, "not yet",
or "stop" returns to the caller with no `Proposal (` block. The
caller re-shows its menu.

## Stop conditions

- **Don't write `journal/` files.** Return conversation text. The
  caller routes it. `manage-ml-backlog` records Backlog rows in
  `JOURNAL.md` when a Proposal is parked; `model-ml-pipeline`
  owns the design note (`scaffold --journal --stem` and
  `design consent`).
- **Don't infer source content from memory.** If the user
  references an article, an issue, or a file, fetch / read it.
  Don't reconstruct from a title or a one-line description.
- **A topic with no artifact is not this skill's search.** Load
  `iterate-from-literature` only if
  `status.skills.iterate-from-literature` is true. Otherwise
  one-line skip and stay here for the question or the idea. Do
  not `WebSearch` for a paper.
- **Confirm before a Proposal.** Emit the synthesis question
  **before** any `Proposal (...)` block. Free-text "hmm" / "maybe"
  / "interesting" / "not yet" is not confirmation. See § Confirm
  before returning.
- **Check `gh` auth before fetching anything from GitHub.** Before
  any `gh issue view` / `gh api` call, run `gh auth status`
  (cheap, cached). If unauthenticated, ask the user to run
  `gh auth login` themselves (suggest `! gh auth login` in the
  prompt) or paste the issue body directly. A failed `gh` call
  surfaces a confusing error; the auth check makes the failure
  mode explicit.
- **Flag goal shifts before returning.** If the user's idea (or
  the source) materially changes the **project goal** as recorded
  in `JOURNAL.md` Status — different output shape (point estimate →
  prediction interval), different downstream consumer (offline
  batch → online serving), different metric class (squared error →
  coverage) — surface it as a question *before* returning the
  Proposal: *"this would update JOURNAL.md Status from <X> to <Y>;
  confirm or amend the goal first?"* The design note should not
  silently redefine success while the Status block still reflects
  the old goal.
- **New dependencies are gated, not assumed.** If a source uses a
  library outside the project's existing env and the user has
  **not** confirmed adding it (e.g. an article uses `lightgbm` /
  `pytorch` / `jax`), do **not** silently include it in
  `Method outline`. Flag it as an open gap (`"this approach needs
  <library>; OK to add?"`) and wait. Until the user answers, the
  library name lives **only** under `Open gaps` — never in
  `Method outline`.
  If the user **already asked to add** a named library, put it in
  `Method outline` and load `add-python-package` when that skill
  is installed. Do not offer a stack substitute (HistGradientBoosting,
  ruff, …) and do not `pixi add` / `env add` from this skill.
- **Domain-specific assertions need user confirmation.** If the
  source asserts something the article / issue / spec alone can't
  establish for *our* dataset — e.g. "feature X is monotone in the
  target," "interaction Y matters for this asset class," "metric Z
  is right because the use case is one-sided" — list each
  assertion in `Open gaps` and ask the user before returning. Don't
  ship paper-flavored guesses as facts.
- **Harness-level "no clarifying questions" instructions do not
  apply to this skill's confirmation gates.** The entry-point
  `AskUserQuestion` (free-text / artifact) and the § "Confirm
  before returning" synthesis gate are operating-contract gates,
  not clarifying questions. They fire regardless of any
  harness-level hint. The synthesis gate is non-skippable when a
  Proposal is the outcome — even when the user's intent feels
  "obvious". See the project's `CLAUDE.md` § "Skill consultation
  contract" rule 3.

## Questions about this project

When the user asks about the current workspace rather than handing
over an idea or an artifact, answer from `JOURNAL.md` Status and
History, the EDA summary in `data_analysis/data_analysis.md` when
it exists, and the last History headline. Leave a metric as `n/a`
when neither the digest nor the user supplied it. Do not invent
numbers. This turn is complete with no Proposal. Return to the
caller.

## The entry-point AskUserQuestion

When this skill is invoked and the entry is not already resolved,
open with `AskUserQuestion` — two mutually exclusive options, no
silent default:

- **free-text** — the user has a verbal or written idea, or a
  question, and will describe it directly.
- **artifact** — the user has a URL, a GitHub issue, a spec file,
  a notes repo, or another concrete artifact. The agent reads it,
  summarizes through the three-question lens, and confirms.

Use the canonical `AskUserQuestion` UI; only fall back to plain-
text enumeration if it is genuinely unavailable in the current
session.

**Exception — pre-resolved entry point.** When the caller already
resolved the branch (the user typed a URL, an issue link, or a
concrete idea), skip this AskUserQuestion and go straight to that
branch. The synthesis-confirmation gate still fires when the
outcome is a Proposal.

The same exception applies when `model-ml-pipeline`'s **Discuss
the next step** branch has already produced an open conversation
and a concrete idea. Skip the free-text / artifact menu; apply
the three shaping questions and confirmation gate directly to the
agreed idea. If the discussion ends without an idea, return to
the caller and emit no Proposal.

## The three shaping questions

Every Proposal returned from this skill must answer:

1. **What are we trying to learn?** (turns "try X" into a
   hypothesis)
2. **Why now?** (the specific reason this idea surfaced — quote
   the user, link the article, cite the issue / file)
3. **What changes vs. the previous experiment?** (which file in
   `src/<pkg>/` is touched, in prose — not code)

Missing → ask the user. Don't fabricate. There is no fourth
"how will we know it worked" question — acceptance criteria are
out of scope for this skill. A question-only turn does not need
these three answers.

## The two branches

### Branch A — artifact

The user picks `artifact`, or a URL / issue / path is already in
hand. A topic with no URL, issue, or path is not this branch:
load `iterate-from-literature` when that skill is installed.

- A **paper, blog, or doc URL**: **Fetch with `WebFetch`**. Read
  the abstract and the section most relevant to the technique.
  Do not `WebSearch` to locate a paper from a topic alone.
- A **GitHub issue**: run the resolution priority below, then
  `gh issue view <N> --json title,body,labels,url` (and pull the
  most recent ~5 comments via `--json …,comments` or
  `gh api repos/<owner>/<repo>/issues/<N>/comments` if the body is
  under-specified — the proposal often lives in the thread).
- A **spec file / notes file**: `Read` the file the user named;
  don't crawl neighbors.
- A **reference repo**: read `README.md` / `SPEC.md` / `NOTES.md`
  or whichever top-level proposal doc the user named. Don't crawl
  the whole tree — that hides the signal.

**GitHub-issue resolution priority** (never silently guess the
repo):

1. **Explicit URL** in the user's message
   (`https://github.com/<owner>/<repo>/issues/<N>`) — wins
   unconditionally.
2. **`org/repo#N` shorthand** (`probabl-ai/skore#42`) — wins over
   current context.
3. **Bare `#N` or "issue 42"** with no qualifier — fall back to
   the current `gh` context (`gh repo view --json
   nameWithOwner` to confirm). If nothing, ask the user before
   fetching.

Then:

1. **Map to the three shaping questions.** What does the artifact
   propose? What concretely changes in `src/<pkg>/`? Quote it for
   "why now?".
2. **Cite specifically.** `Source` is the URL with the claim, the
   issue URL, or the file path and line numbers.
3. **Surface transfer risks** and **domain assertions** in
   `Open gaps` (`[needs user confirmation]` for claims this
   dataset does not establish).
4. **Flag new dependencies as open gaps**, not as silent additions
   to `Method outline` (Stop conditions, above).
5. **Confirm before returning** — see § Confirm before returning.

**If fetch cannot run this turn** (no tools, unreachable URL):
still emit the three shaping questions (placeholders are fine),
put domain claims under `Open gaps` with `[needs user
confirmation]`, and show the confirmation restatement. Do not
wait on the fetched body to skip those boxes. For a GitHub issue,
still name `gh auth status` then `gh issue view <N> …`.

### Branch B — free-text

The user picks `free-text`, or types an idea directly.

1. If it is a question about this project, follow § Questions
   about this project and return with no Proposal.
2. If it is a topic with no artifact ("what do people do for
   censored regression?"), load `iterate-from-literature` when
   installed. Otherwise one-line skip and stay on the idea or
   the question.
3. **Walk the three shaping questions in plain language.** Quote
   the user when summarizing so the framing stays theirs.
4. **Treat their words as the `Source`.** The Proposal's `Source`
   field is the user quote (or a one-sentence paraphrase the user
   has approved).
5. **Confirm before returning.**

## Confirm before returning

Before handing a Proposal back to the caller, emit a short
plain-text synthesis and wait for explicit approval:

> "From <source>, I understand you'd like to **<one-line
> intent>** — concretely, change `src/<pkg>/<file>.py` to
> **<method-outline-summary>**. Open gaps: **<bullets>**. Does
> this capture what you want before I hand it back?"

Until the user says yes, the message is **only** that quoted
paragraph. Do not emit a `Proposal (` header, even labeled
PENDING / NOT RETURNED.

The user's answer determines what happens next:

- **"Yes / confirm / go" → return the Proposal.** Do not emit the
  `Proposal (...)` block before this yes. Do not write
  `journal/NN_*.md`. `model-ml-pipeline` drafts that note after
  Draft.
- **"No / not quite / adjust X" → revise and re-confirm.** Do not
  return a Proposal the user hasn't signed off on.
- **"Not yet" / "stop" / the turn was only a question → no
  Proposal.** Return to the caller.

Show the restatement even when the source body was not fetched
this turn, whenever the intended outcome is a Proposal.

## What is returned

Either no Proposal, or this block:

```
Proposal (from: user via <artifact | free-text>):
  Question:        <one sentence>
  Motivation:      <quote / URL / file path + the why-now reason>
  Source:          <article URL with claim | gh issue URL | spec file:line | user quote>
  Method outline:  <prose; which file in src/<pkg>/ is touched>
  Open gaps:       <transfer risks, dep questions, domain assertions
                    needing user confirmation, anything the source
                    didn't answer>
```

**No `Success` field.** The caller asks Draft, Park, or Stop.
`model-ml-pipeline` owns the design note and approval gate.

## Companion skills

- **`explore-ml-directions`** — usual caller; owns Draft / Park /
  Stop.
- **`iterate-from-literature`** — topic with no artifact.
- **`iterate-from-skore`** — mines the previous audit digest.
- **`manage-ml-backlog`** — may call this skill; writes Backlog
  rows when the user parks a Proposal.
- **`model-ml-pipeline`** — Discuss loads this skill once an idea
  is agreed; owns design-note creation after Draft.
- **`add-python-package`** — when the user already asked to add a
  named library.
- **`build-ml-pipeline`** / **`evaluate-ml-pipeline`** — owners
  of the files under `src/<pkg>/` and `experiments/NN_*.py` that
  the `Method outline` will eventually touch.
