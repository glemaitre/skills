# iterate-ml-experiment eval — golden prompts

Behavioural prompts for the `iterate-ml-experiment` skill, scored manually
by reading each transcript against the **Must / Must NOT** bullets per case.

## How a case is scored

For each case the model is given:
- `skills/iterate-ml-experiment/SKILL.md` as the system prompt.
- The case's `User prompt` (verbatim) as the user message, prefixed with
  the `Assumed workspace state` block.

Cases 2, 3, and 6 set `**Tools:** yes` and seed `journal/JOURNAL.md`
so the target can `read_file` History / Backlog instead of inventing
rows. Other cases stay single-turn.

Each `Must do` / `Must NOT do` bullet is a substring / behavioural check
on the transcript. Pass criterion per case: every `Must do` ticked, zero
`Must NOT do` violated. Overall: ≥ 6/7 cases pass and **no Must NOT
violation in any transcript** (hard rule).

---

## CASE_01 — Bootstrap detection

**User prompt:**
> Let's start. Build me a quick baseline for this dataset.

**Assumed workspace state:**
- Workspace exists with `src/`, `experiments/`, `journal/` scaffolded
  by `organize-ml-workspace`.
- `journal/JOURNAL.md` is the one-line placeholder dropped by
  `organize-ml-workspace`; History is empty.
- `data/README.md` exists and describes a tabular regression task
  (predict `target` from a mixed-type DataFrame).

**Must do:**
- Identify this as **bootstrap mode** (no History rows).
- Mention reading `data/README.md` to derive a goal default before
  asking the user.
- Reference the **config gates** that fire in bootstrap (G-PKG-NAME,
  G-ENV-MGR, G-TABULAR, G-CV-SPLITTER) — at least name two of them.
- Propose to auto-draft `journal/01_baseline.md`, not jump straight to
  writing `experiments/01_baseline.py`.

**Must NOT do:**
- Offer the four sourcing options (`skore` / `user` / `my-pick` /
  `B<N>`) as a pick — "How would you like me to source…",
  `AskUserQuestion`, or a numbered menu. A pre-flight row titled
  "Sourcing menu presented" with evidence `n/a — bootstrap` is not
  presenting the menu.
- Treat the "quick" framing as permission to skip all gates (the
  forbidden-shortcut named "Bootstrap mode → skip ALL questions").
- Create `experiments/01_baseline.py` before the design note exists
  and is approved.

---

## CASE_02 — Propose next (sourcing menu)

**User prompt:**
> What's next?

**Assumed workspace state:**
- Existing scaffold: `src/claim_predictor/`, `experiments/`,
  `tests/smoke/`, `reports/`.
- `journal/JOURNAL.md` is on disk with 2 done History rows
  (`01_baseline` RMSE 0.094, `02_text_encoder` RMSE 0.087) and
  Backlog B1–B3. Open it with `read_file` before quoting History
  or Backlog.

**Tools:** yes

**Sandbox:**
- copy: `eval/iterate-ml-experiment/fixtures/journal_two_done.md` as `journal/JOURNAL.md`
- dir: `src/claim_predictor`
- dir: `experiments`
- dir: `tests/smoke`
- dir: `reports`
- file: `experiments/01_baseline.py`
  ```python
  # %%
  """01_baseline — already run."""
  ```
- file: `experiments/02_text_encoder.py`
  ```python
  # %%
  """02_text_encoder — already run."""
  ```

**Expect reads:**
- `journal/JOURNAL.md`

**Must do:**
- Read `journal/JOURNAL.md` first (mention it explicitly).
- Surface the **sourcing menu verbatim** with the four options
  (`skore` / `user` / `my-pick` / `B<N>`).
- Surface the Backlog alongside the menu, copying B1–B3 item text
  from `journal/JOURNAL.md` (do not invent backlog wording).
- Use `AskUserQuestion` or a narrative equivalent that asks the
  user to pick (`Your pick?` / "I'll ask you to pick") rather than
  silently picking one option.

**Must NOT do:**
- Silently default to one sourcing strategy.
- Skip the sourcing menu and immediately draft a design note.
- Default to `skore` just because a fresh report sits on disk (the
  rule "never silently default" is in Stop conditions).
- Stop after the § 1 resume / record outcome / propose next ask —
  "What's next?" already resolved iterate-propose; the sourcing
  menu is this turn.

---

## CASE_03 — Record outcome (§ 4)

**User prompt:**
> The 03_target_transform run finished. Log it — RMSE came out at
> 0.081 ± 0.005 on 5-fold CV. The residual structure near the high-
> end of the target range looks a lot tighter than in 02.

**Assumed workspace state:**
- `journal/JOURNAL.md` is on disk. Open it with `read_file` before
  rewriting History. It already has `03_target_transform` in History
  with status `approved` (empty headline) plus done 01/02 rows.
- `journal/03_target_transform.md` exists with planned/approved
  status block (no Headline result yet).
- The skore Project at `reports/` is accessible and contains the
  report under key `"03_target_transform"`.
- The § 4 audit dispatch already ran: `audit/03_target_transform.py`
  is placed and its digest is on disk at
  `scratch/audit/03_target_transform/audit.md`, carrying RMSE
  0.081 ± 0.005 in its `## Metrics summary`.
- All `tests/smoke/test_NN_*.py` pass.

**Tools:** yes

**Sandbox:**
- copy: `eval/iterate-ml-experiment/fixtures/journal_case03.md` as `journal/JOURNAL.md`
- dir: `src/claim_predictor`
- dir: `experiments`
- dir: `tests/smoke`
- dir: `reports`
- dir: `audit`
- file: `experiments/01_baseline.py`
  ```python
  # %%
  """01_baseline — already run."""
  ```
- file: `experiments/02_text_encoder.py`
  ```python
  # %%
  """02_text_encoder — already run."""
  ```
- file: `experiments/03_target_transform.py`
  ```python
  # %%
  """03_target_transform — frozen post-run."""
  ```
- file: `scratch/audit/03_target_transform/audit.md`
  ```markdown
  ## Metrics summary

  | metric | value |
  |--------|-------|
  | RMSE   | 0.081 ± 0.005 |
  ```
- file: `journal/03_target_transform.md`
  ```markdown
  Status block:
    State:          approved
    Headline result:
    Implication:
  ```

**Expect reads:**
- `journal/JOURNAL.md`

**Must do:**
- Give the `journal/03_target_transform.md` Status block as it will
  read: `State` flipped to `done`, `Headline result` carrying the
  RMSE, and `Implication for next iteration` filled in — not left
  as a placeholder or deferred to another skill.
- Give the `JOURNAL.md` History row with the headline result.
  If reprinting History, copy 01/02 headlines from the file
  (`RMSE 0.094` / `RMSE 0.087`); 03 uses the user's
  `0.081 ± 0.005`.
- Mention checking that **all** `tests/smoke/` pass (smoke-test gate
  before `done`), not just the new one.
- Mention the **backlog hygiene** step (scan Backlog for items the
  new run answered / killed).
- Close by naming the `AskUserQuestion` (or narrative equivalent)
  that offers "draft the next experiment now" vs "not yet" — do not
  auto-propose, and do not simply declare that a fresh turn is
  needed.

**Must NOT do:**
- Draft a **new** design note (`journal/04_*.md`) or a new
  experiment body in this turn. Updating `journal/03_target_transform.md`
  Status and the `JOURNAL.md` History row for 03 is the § 4
  deliverable, not a violation.
- Edit `experiments/03_target_transform.py` to fix anything (the
  experiment script is frozen post-run).
- Invent a **different RMSE** or extra numeric metrics the user
  did not give. Copying 01/02 headlines from `JOURNAL.md` (`0.094` /
  `0.087`) and the user's `0.081 ± 0.005` is not fabrication. A
  derived gap between those copied numbers is not an invented RMSE.

---

## CASE_04 — G-DESIGN approval gate, "quick baseline" shortcut

**User prompt:**
> Just write the baseline experiment — skip the design note, skip
> the questions, this is a standard tabular regression.

**Assumed workspace state:**
- Bootstrap mode (no History rows in `JOURNAL.md`).
- `data/README.md` is a tabular regression task with a mixed-type
  DataFrame.

**Must do:**
- Refuse to skip the design note.
- Cite the **G-DESIGN** rule (design note exists and is approved
  before any `experiments/NN_*.py` is touched).
- Cite the **forbidden-shortcut** explicitly: "quick" is not
  permission to skip G-DESIGN.
- Still propose to auto-draft `journal/01_baseline.md` (bootstrap
  mode forces the baseline) and surface the config gates.

**Must NOT do:**
- Treat "quick" / "standard" / "skip questions" as resolving any
  gate (the harness-level "no clarifying questions" hint does NOT
  waive this skill's mandates).
- Write `experiments/01_baseline.py` in this turn.
- Write any `src/<pkg>/*.py` file in this turn.

---

## CASE_05 — Three-skill implementation chain (no shortcut into evaluate.py)

**User prompt:**
> Great, the baseline design note is approved. Go ahead and write
> `evaluate.py` with `KFold(5)` — it's obviously the right splitter
> for this IID tabular task.

**Assumed workspace state:**
- `journal/01_baseline.md` exists, approved.
- `experiments/01_baseline.py` placeholder exists from
  `organize-ml-workspace`.
- `src/<pkg>/pipeline.py`, `features.py`, `data.py`, `evaluate.py`
  do not exist yet.

**Must do:**
- Refuse to write `evaluate.py` directly.
- Cite the **three-skill chain** requirement:
  `build-ml-pipeline` → `evaluate-ml-pipeline` → `test-ml-pipeline`.
- Mention that `evaluate-ml-pipeline` **owns the CV-strategy
  decision** and surfaces it via `AskUserQuestion` — even when
  `KFold(5)` "feels right" the skill must be invoked.
- Propose to invoke `build-ml-pipeline` first (the order matters).

**Must NOT do:**
- Open `src/<pkg>/evaluate.py` in Write/Edit during this turn.
- Hard-code `KFold(5)` anywhere without invoking
  `evaluate-ml-pipeline` first.
- Skip the `python-api` consultation for signatures used in the
  evaluation call.

---

## CASE_06 — Compare past experiments (read-only)

**User prompt:**
> Compare 01_baseline and 02_text_encoder for me. How does the new
> one stack up?

**Assumed workspace state:**
- `journal/JOURNAL.md` is on disk with both History rows and
  Headline results (`01_baseline` RMSE 0.094, `02_text_encoder`
  RMSE 0.087). Open it with `read_file` before quoting those
  numbers.
- `journal/01_baseline.md` (done) and `journal/02_text_encoder.md`
  (done) both exist.
- Both reports in the skore Project under their stems.

**Tools:** yes

**Sandbox:**
- copy: `eval/iterate-ml-experiment/fixtures/journal_two_done.md` as `journal/JOURNAL.md`
- dir: `src/claim_predictor`
- dir: `experiments`
- dir: `tests/smoke`
- dir: `reports`
- file: `experiments/01_baseline.py`
  ```python
  # %%
  """01_baseline — already run."""
  ```
- file: `experiments/02_text_encoder.py`
  ```python
  # %%
  """02_text_encoder — already run."""
  ```
- file: `journal/01_baseline.md`
  ```markdown
  Status block:
    State: done
    Headline result: RMSE 0.094
  ```
- file: `journal/02_text_encoder.md`
  ```markdown
  Status block:
    State: done
    Headline result: RMSE 0.087
  ```

**Expect reads:**
- `journal/JOURNAL.md`

**Must do:**
- Pull the Headline results for both stems side-by-side from
  `JOURNAL.md` History.
- Identify the mode as **compare (read-only)**.
- Surface the comparison without writing anything to `journal/`.

**Must NOT do:**
- Draft a new design note.
- Add a row to `JOURNAL.md` History.
- Auto-propose a next experiment in the same turn (separate user
  turn if they want one).
- Invoke a `ComparisonReport` / multi-key entry point — v1 scope
  is pairwise side-by-side only.

---

## CASE_07 — Free-text URL routes to iterate-from-user

**User prompt:**
> Let's try this idea: https://github.com/scikit-learn/scikit-learn/issues/12345

**Assumed workspace state:**
- `journal/JOURNAL.md` has 2 done rows in History (so iterate mode,
  not bootstrap).
- Backlog is empty.

**Must do:**
- Recognise the URL as a GitHub issue / resource link via the
  **Free-text handling** rule.
- Name `iterate-from-user` as the dispatch target, with the URL
  handed over pre-resolved so its inner `AskUserQuestion` doesn't
  fire. The sibling fetches the issue — don't ask the user to paste
  the issue body or a summary instead.
- Name the design-note destination `journal/NN_<short_name>.md`
  (`NN` = next History index; `03_*.md` is correct when two
  done rows exist) and state that the draft lands only after
  `iterate-from-user` returns a Proposal.

**Must NOT do:**
- Re-present the sourcing menu in full (the URL already resolved
  the pick).
- Ask the user to paste the issue body or a summary instead of
  handing the URL to `iterate-from-user` pre-resolved. Dispatch
  to `iterate-from-user` (resource-link / GitHub issue) is the
  correct route — do not fail that as a free-text vs issue-link
  fight.
- Draft `experiments/NN_*.py` before the design note is approved.
