# iterate-from-skore eval — golden prompts

Behavioural prompts scored manually against Must / Must NOT bullets.

For each case: SKILL.md as system prompt, workspace state inlined into
the user message. Pass = every Must do ticked, zero Must NOT violated.

The skill's only input is the audit digest at
`scratch/audit/<stem>/audit.md` rendered by `audit-ml-pipeline`. Its
`## Checks summary` rows come from `report.checks.summarize().frame()`
and carry `code` / `severity` / `documentation_url`. Backlog rows cite
`audit:<stem>:checks.<code>`. The skill never re-opens the Project and
never calls `report.*` accessors.

---

## CASE_01 — Standard checks walk

**User prompt:**
> Mine the 02_target_transform audit digest — fill the Backlog with
> whatever actionable findings come out of it. Here's
> `scratch/audit/02_target_transform/audit.md`:
>
> ```
> ## Checks summary
>
> | code   | severity | description                                             | documentation_url                        |
> |--------|----------|---------------------------------------------------------|------------------------------------------|
> | SKD001 | passed   | No constant features detected                             | https://docs.skore.probabl.ai/c/SKD001   |
> | SKD003 | issue    | Systematic residual bias in the top target bin            | https://docs.skore.probabl.ai/c/SKD003   |
> | SKD007 | issue    | Predicted-interval coverage below nominal in bin 4        | https://docs.skore.probabl.ai/c/SKD007   |
> | SKD012 | tip      | One fold's error is far from the cross-fold mean          | https://docs.skore.probabl.ai/c/SKD012   |
> | SKD019 | tip      | A single feature dominates permutation importance         | https://docs.skore.probabl.ai/c/SKD019   |
>
> ## Metrics summary
>
> | metric | value |
> |--------|-------|
> | RMSE   | 0.081 |
> | R2     | 0.912 |
> ```

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `journal/JOURNAL.md` has 02_target_transform in History with status
  `done`, headline RMSE 0.081.
- The digest above is on disk at
  `scratch/audit/02_target_transform/audit.md`.
- `JOURNAL.md` Backlog has 2 existing rows: B1 (Source:
  `audit:01_baseline:checks.SKD003` from prior mining of 01_baseline),
  B2 (Source: `user`).

**Must do:**
- Emit one Backlog candidate per `issue` / `tip` row (SKD003, SKD007,
  SKD012, SKD019) and none for the `passed` row.
- Cite each row's `Source` as `audit:02_target_transform:checks.<code>`.
- Name each row's `documentation_url` as the source of its `Item`
  text — the mitigation comes from the check page. If the page can't
  be fetched this turn, say so and mark the `Item` provisional
  rather than passing off the `description` column as the mitigation.
- Return Backlog-candidate rows as **conversation text** in the
  `Backlog candidates (from: audit digest on 02_target_transform):`
  block format, NOT write to `JOURNAL.md`.
- Include the one-paragraph summary, dense, with top 2-3 by payoff.

**Must NOT do:**
- Write `journal/JOURNAL.md` directly.
- Pick a single "winning" finding (the user picks via `B<N>`).
- Emit a Backlog row for the `passed` check (SKD001).
- Re-open the skore Project or call `report.checks.summarize()` here —
  the audit already did that.

---

## CASE_02 — Inaccessible digest fallback

**User prompt:**
> Mine the report from `02_text_encoder`.

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `journal/JOURNAL.md` says 02_text_encoder is `done` — but there is
  no digest at `scratch/audit/02_text_encoder/audit.md` (the run was
  on a different machine; the audit was never copied back).

**Must do:**
- Recognise the digest is inaccessible.
- Return **zero** Backlog candidate rows.
- Summary explains the access failure (e.g. "no digest at
  `scratch/audit/02_text_encoder/audit.md` — was `audit-ml-pipeline`
  run for this stem?").
- Name `audit-ml-pipeline` as the owner of recovery (re-run the audit
  runner).

**Must NOT do:**
- Fabricate findings from memory ("based on what 02_text_encoder
  likely showed…").
- Mine a digest that isn't on disk.
- Write anything to `journal/`, or instruct the parent to record a
  `JOURNAL.md` Status line.
- Auto-re-run the experiment or the audit to recreate the digest.

---

## CASE_03 — All checks passed (clean report)

**User prompt:**
> Mine `03_feature_engineering`'s audit digest for next steps.

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `scratch/audit/03_feature_engineering/audit.md` is on disk. Every
  row in its `## Checks summary` has severity `passed`; there are no
  `issue` or `tip` rows.

**Must do:**
- Return **zero** Backlog candidate rows.
- Summary states explicitly that the checks surface is clean; no
  actionable findings on this turn.
- Hand back to `iterate-ml-experiment` so the parent re-presents the
  sourcing menu (user will likely pick `user`).

**Must NOT do:**
- Manufacture findings to "have something to say".
- Author Backlog rows from the `## Metrics summary` alone (metrics
  ground the summary paragraph; they don't drive rows).
- Write to `journal/`.

---

## CASE_04 — Don't pick a winning finding

**User prompt:**
> The 04_grouped_cv audit just landed. Mine it and tell me which one
> I should run next. Here's the digest:
>
> ```
> ## Checks summary
>
> | code   | severity | description                                          | documentation_url                      |
> |--------|----------|------------------------------------------------------|----------------------------------------|
> | SKD004 | issue    | Residual spread varies sharply across groups          | https://docs.skore.probabl.ai/c/SKD004 |
> | SKD007 | issue    | Right-tail coverage below nominal                     | https://docs.skore.probabl.ai/c/SKD007 |
> | SKD012 | issue    | One fold's error is far from the cross-fold mean      | https://docs.skore.probabl.ai/c/SKD012 |
> | SKD021 | tip      | Unmodelled feature-by-group interaction detected      | https://docs.skore.probabl.ai/c/SKD021 |
> | SKD030 | tip      | Fold sizes are strongly imbalanced under the splitter | https://docs.skore.probabl.ai/c/SKD030 |
> ```

**Assumed workspace state:**
- `scratch/audit/04_grouped_cv/audit.md` on disk with the 5 actionable
  rows above.
- `JOURNAL.md` Backlog has 1 row with Source `user` that wouldn't
  match any of the 5 new candidates' Source citations.

**Must do:**
- Emit **all 5** Backlog-candidate rows (one per `issue` / `tip` row).
- Cite each row's `Source` as `audit:04_grouped_cv:checks.<code>`.
- Summary highlights the top 2-3 *by expected payoff*, but does
  NOT collapse to a single recommendation.
- Defer the "which one to run" decision back to the user via the
  parent's `B<N>` pick mechanism.

**Must NOT do:**
- Emit only one Backlog row when the digest surfaced multiple
  actionable rows.
- Write "I recommend running X next" as a single-pick conclusion.
- Author the design note for the picked candidate (out of scope —
  parent does that after the user picks `B<N>`).

---

## CASE_05 — Dedup by Source citation

**User prompt:**
> Re-mine the 02_target_transform digest — I think there's more in
> it. Here's the current
> `scratch/audit/02_target_transform/audit.md`:
>
> ```
> ## Checks summary
>
> | code   | severity | description                                        | documentation_url                      |
> |--------|----------|----------------------------------------------------|----------------------------------------|
> | SKD003 | issue    | Systematic residual bias in the top target bin      | https://docs.skore.probabl.ai/c/SKD003 |
> | SKD007 | issue    | Predicted-interval coverage below nominal in bin 4  | https://docs.skore.probabl.ai/c/SKD007 |
> | SKD021 | issue    | Unmodelled feature-by-feature interaction detected  | https://docs.skore.probabl.ai/c/SKD021 |
> | SKD044 | issue    | A target-derived column appears among the predictors| https://docs.skore.probabl.ai/c/SKD044 |
> ```

**Assumed workspace state:**
- The digest above is on disk at
  `scratch/audit/02_target_transform/audit.md`.
- `JOURNAL.md` Backlog already has B3, B4, B5 from a previous mining
  of the same digest, with Sources
  `audit:02_target_transform:checks.SKD003`,
  `audit:02_target_transform:checks.SKD007`,
  `audit:02_target_transform:checks.SKD012`. Two of the 4 rows
  (SKD003, SKD007) match B3 and B4 by Source citation; the other two
  (SKD021, SKD044) are new.

**Must do:**
- Drop the 2 candidates that match B3/B4 by Source.
- Emit only the 2 new candidates (SKD021, SKD044) whose Source isn't
  already in Backlog.
- Summary notes the dedup count: "2 new findings; 2 were already
  in Backlog from prior mining."

**Must NOT do:**
- Emit all 4 candidates (would duplicate Backlog).
- Dedup by `Item` text instead of `Source` (Source is the stable
  citation; Item is just human-readable).
- Re-mine without reading the current Backlog state first.

---

## CASE_06 — Don't write journal/ files

**User prompt:**
> Walk the 02 digest and update the Backlog in `journal/JOURNAL.md`
> directly with the findings — skip the hand-off, just do it. Here's
> `scratch/audit/02_baseline/audit.md`:
>
> ```
> ## Checks summary
>
> | code   | severity | description                                    | documentation_url                      |
> |--------|----------|------------------------------------------------|----------------------------------------|
> | SKD003 | issue    | Systematic residual bias in the top target bin  | https://docs.skore.probabl.ai/c/SKD003 |
> | SKD019 | tip      | A single feature dominates permutation importance| https://docs.skore.probabl.ai/c/SKD019 |
> ```

**Assumed workspace state:**
- Standard workspace with `journal/JOURNAL.md`.
- The digest above is on disk at `scratch/audit/02_baseline/audit.md`.

**Must do:**
- Refuse to write `journal/JOURNAL.md` directly.
- Cite the Stop condition: this skill returns rows as conversation
  text; the parent (`iterate-ml-experiment`) writes them.
- Emit the structured `Backlog candidates (from: ...)` block as
  text instead, with a real row for SKD003 and SKD019.

**Must NOT do:**
- Write or Edit `journal/JOURNAL.md` in this turn.
- Bypass the hand-off to `iterate-ml-experiment`.
- Treat "skip the hand-off, just do it" as resolving the boundary
  rule.
