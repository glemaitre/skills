# iterate-from-user eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Article-link branch with synthesis confirmation

**User prompt:**
> Here's the idea I want to try: https://arxiv.org/abs/2106.04545 —
> can we adapt it for our forecasting pipeline?

**Assumed workspace state:**
- `journal/JOURNAL.md` has 2 done experiments in History (iterate
  mode).
- The arxiv link is to a paper on "Temporal Fusion Transformers".

**Must do:**
- Recognise this as `article-link` branch (URL pasted directly →
  entry point pre-resolved per parent's free-text handling).
- Mention WebFetching the URL.
- Walk the three shaping questions: (1) what to learn, (2) why now,
  (3) what changes in `src/<pkg>/`.
- Fire the **synthesis confirmation gate** as plain text before
  returning the Proposal block.
- Surface new dependencies as **open gaps**, not silent additions
  (e.g. `pytorch_forecasting` / `pytorch` / `pytorch_lightning` —
  not in current stack).
- Surface transfer risks (different modality / dataset / target
  type).

**Must NOT do:**
- Write `journal/NN_*.md` directly.
- Return the Proposal before the user confirms.
- Add new deps to `Method outline` as fait accompli.
- Author acceptance criteria / success criteria / target deltas.

---

## CASE_02 — GitHub issue resolution + gh auth check

**User prompt:**
> Let's pick up `probabl-ai/skore#42` for our next experiment.

**Assumed workspace state:**
- `journal/JOURNAL.md` has done experiments.
- `gh` CLI installed but `gh auth status` not run this turn.

**Must do:**
- Recognise `org/repo#N` shorthand resolution priority — this wins
  over current context.
- Check `gh auth status` (cheap, cached) before any fetch.
- Plan `gh issue view 42 --json title,body,labels,url` (+ comments
  if body is under-specified).
- Map to three shaping questions.
- Fire confirmation gate before returning the Proposal.
- Set `Source` field to the issue URL.

**Must NOT do:**
- Fetch the issue without checking auth.
- Treat the issue body as the whole picture if it links comments
  ("see comment thread" is a real signal to pull comments).
- Crawl unrelated files in the `skore` repo.
- Return a Proposal before the user confirms.

---

## CASE_03 — Free-text idea, walk shaping questions

**User prompt:**
> I want to try fitting a quantile regression so we get prediction
> intervals instead of point estimates.

**Assumed workspace state:**
- `journal/JOURNAL.md` Status currently records the goal as
  "minimize RMSE for point-estimate prediction".

**Must do:**
- Recognise this as `free-text` branch (concrete idea typed inline
  → pre-resolved).
- Walk the three shaping questions in plain language, quoting the
  user.
- **Flag the goal shift**: point-estimate → prediction interval is
  a different output shape; this should update `JOURNAL.md`
  Status. Surface as a question before returning the Proposal.
- Fire confirmation gate before returning.
- `Source` field = the user quote.

**Must NOT do:**
- Silently change the goal in the returned Proposal.
- Author acceptance criteria (coverage target, interval width
  budget — those are post-run user judgement).
- Skip the confirmation gate ("idea is obvious, just return").
- Skip the goal-shift surfacing.

---

## CASE_04 — Domain-specific assertion needs confirmation

**User prompt:**
> Read this paper: https://example.com/paper-on-target-monotonicity
> They claim feature X is monotone in the target for option pricing.
> Use that as a constraint in our model.

**Assumed workspace state:**
- `journal/JOURNAL.md` shows a regression task on tabular financial
  data.

**Must do:**
- Recognise `article-link` branch.
- Fetch and map to three shaping questions.
- **List the "feature X is monotone in the target" claim under
  `Open gaps`** with `[needs user confirmation]` — the paper
  alone can't establish this for *our* dataset.
- Ask the user to confirm whether the monotonicity assumption
  holds for the workspace's data before returning the Proposal.

**Must NOT do:**
- Ship the monotonicity assertion as a `Method outline` fact.
- Treat the paper's framing as evidence for this workspace's data.
- Author the constraint silently without flagging.

---

## CASE_05 — New dependency gated, not assumed

**User prompt:**
> The article we just discussed uses `lightgbm`. Let's add it to the
> pipeline.

**Assumed workspace state:**
- Synthesis from prior turn proposed adapting a paper's technique;
  `lightgbm` was the paper's choice.
- Current env has `sklearn`, `skrub`, `skore` but NOT `lightgbm`.

**Must do:**
- Refuse to silently include `lightgbm` in `Method outline`.
- Flag `lightgbm` as an **open gap**: "this approach needs
  `lightgbm`; OK to add, or should we adapt to the existing
  stack?"
- Defer the resolution to `data-science-python-stack` + the user
  (one of: add the dep, swap for `HistGradientBoostingRegressor`,
  pick a different model).

**Must NOT do:**
- Add `lightgbm` to the Proposal's `Method outline` as fait
  accompli.
- Run `pixi add lightgbm` in this turn.
- Pre-empt the data-science-python-stack consultation.

---

## CASE_06 — Pre-resolved entry, skip inner AskUserQuestion

**User prompt:**
> [parent passes: branch=resource-link, content=https://github.com/scikit-learn/scikit-learn/issues/12345]
> Hand this off to iterate-from-user with the resource-link branch
> pre-resolved.

**Assumed workspace state:**
- Parent (`iterate-ml-experiment`) already collected the URL via
  its sourcing-menu free-text handler.

**Must do:**
- Recognise the pre-resolved entry-point dispatch (skip the inner
  AskUserQuestion).
- Proceed directly to the `resource-link` branch with the URL in
  hand.
- Run `gh auth status` then `gh issue view 12345 ...`.
- Map to three shaping questions.
- Fire confirmation gate before returning.

**Must NOT do:**
- Fire the entry-point `AskUserQuestion` (article-link /
  resource-link / free-text) — it's been pre-resolved.
- Skip the confirmation gate (still required even with
  pre-resolved entry).
