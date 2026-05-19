# iterate-from-skore eval — golden prompts

Behavioural prompts scored manually against Must / Must NOT bullets.

For each case: SKILL.md as system prompt, workspace state inlined into
the user message. Pass = every Must do ticked, zero Must NOT violated.

---

## CASE_01 — Standard diagnosis walk

**User prompt:**
> Mine the 02_target_transform skore report — fill the Backlog with
> whatever actionable findings come out of it. I've already run the
> scratch probe; here's `report.diagnosis()` output:
>
> ```
> {
>   "residuals.by_target_bin": "systematic positive bias in bin>0.95 (n=412); residuals mean +0.018 vs grand mean +0.0003",
>   "calibration.bin_4_underconfident": "predicted-interval coverage 78% vs nominal 90% in bin 4 (target range 0.6-0.8)",
>   "metrics.fold_3_outlier": "fold 3 RMSE 0.121 vs cross-fold mean 0.081; same fold has 2x feature_2 variance",
>   "feature_importance.target_log_dominance": "target_log permutation importance 0.42; next-highest feature 0.08 — pipeline may be over-relying on the log transform"
> }
> ```

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `journal/JOURNAL.md` has 02_target_transform in History with status
  `done`, headline RMSE 0.081.
- `reports/` contains the skore Project; 02_target_transform's report
  is accessible.
- `JOURNAL.md` Backlog has 2 existing rows: B1 (Source:
  `diagnosis:residuals.by_target_bin` from prior mining of 01_baseline),
  B2 (Source: `user`).
- `scratch/api/skore/0.18.0/evaluate.md` cached.

**Must do:**
- Mention opening the skore Project via `python-api` consultation
  (not from memory).
- Mention calling `report.diagnosis()` on the 02_target_transform
  report.
- Mention dedup against `JOURNAL.md` Backlog by `Source` citation —
  any candidate whose Source matches B1's `diagnosis:residuals.by_target_bin`
  must be dropped.
- Return Backlog-candidate rows as **conversation text** in the
  `Backlog candidates (from: skore diagnosis on 02_target_transform):`
  block format, NOT write to `JOURNAL.md`.
- Include the one-paragraph summary, dense, with top 2-3 by payoff.

**Must NOT do:**
- Write `journal/JOURNAL.md` directly.
- Pick a single "winning" finding (the user picks via `B<N>`).
- Fabricate findings from memory before/instead of calling
  `report.diagnosis()`.
- Use inline `pixi run python -c "..."` for the diagnosis walk
  (all Python goes to scratch).

---

## CASE_02 — Inaccessible report fallback

**User prompt:**
> Mine the report from `02_text_encoder`.

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `journal/JOURNAL.md` says 02_text_encoder is `done` — but the
  skore Project store at `reports/` is empty (the run was on a
  different machine; report wasn't copied back).

**Must do:**
- Recognise the report is inaccessible.
- Return **zero** Backlog candidate rows.
- Summary explains the access failure (e.g. "skore Project store at
  `reports/` not found — was the experiment run? was the key
  spelled right?").
- Hand back to `iterate-ml-experiment` so the parent can surface
  the gap.

**Must NOT do:**
- Fabricate findings from memory ("based on what 02_text_encoder
  likely showed…").
- Walk a report that isn't on disk.
- Write anything to `journal/`.
- Auto-re-run the experiment to recreate the report.

---

## CASE_03 — Empty diagnosis (clean report)

**User prompt:**
> Mine `03_feature_engineering`'s report for next steps.

**Assumed workspace state:**
- `skore` installed at 0.18.0.
- `03_feature_engineering` report is accessible at `reports/`.
- `report.diagnosis()` returns no actionable findings (calibration,
  residuals, per-slice metrics all look clean within sample-size
  limits).

**Must do:**
- Return **zero** Backlog candidate rows.
- Summary states explicitly that the report looks clean on
  metric / calibration / residuals; no actionable findings.
- Hand back to `iterate-ml-experiment` so the parent can note the
  clean diagnosis in `JOURNAL.md` Status and re-present the
  sourcing menu (user will likely pick `user`).

**Must NOT do:**
- Manufacture findings to "have something to say".
- Author Backlog rows for marginal noise (e.g. a 5-row slice with
  miscalibration is NOT actionable per the skill's rule).
- Write to `journal/`.

---

## CASE_04 — Don't pick a winning finding

**User prompt:**
> The 04_grouped_cv report just landed. Mine it and tell me which
> one I should run next. I've already run the probe; here's the
> output:
>
> ```
> {
>   "residuals.by_group": "groups {17, 42, 88} have residual std 2.3x the cross-group mean — group-specific feature distributions diverge",
>   "calibration.tail_underconfidence": "right-tail (target>0.92) coverage 71% vs nominal 90%",
>   "metrics.group_3_outlier_fold": "fold containing group 88 has RMSE 0.18 vs 0.094 elsewhere",
>   "feature_interactions.cross_group_signal": "feature_3 × group interaction explains 18% of grouped variance currently unmodeled",
>   "splitter.train_test_size_imbalance": "GroupKFold yields fold-size range [42, 318]; smaller folds may need stratification or refit"
> }
> ```

**Assumed workspace state:**
- `04_grouped_cv` report accessible; `report.diagnosis()` returns 5
  actionable findings (shown above).
- `JOURNAL.md` Backlog has 1 row with Source `user` that wouldn't
  match any of the 5 new candidates' Source citations.

**Must do:**
- Emit **all 5** Backlog-candidate rows (one per actionable finding).
- Cite each row's `Source` as `diagnosis:<path>`.
- Summary highlights the top 2-3 *by expected payoff*, but does
  NOT collapse to a single recommendation.
- Defer the "which one to run" decision back to the user via the
  parent's `B<N>` pick mechanism.

**Must NOT do:**
- Emit only one Backlog row when the diagnosis surfaced multiple
  actionable findings.
- Write "I recommend running X next" as a single-pick conclusion.
- Author the design note for the picked candidate (out of scope —
  parent does that after the user picks `B<N>`).

---

## CASE_05 — Dedup by Source citation

**User prompt:**
> Re-mine the 02_target_transform report — I think there's more in
> it. Here's `report.diagnosis()` from my fresh probe:
>
> ```
> {
>   "residuals.by_target_bin": "systematic positive bias in bin>0.95 (n=412); residuals mean +0.018",
>   "calibration.bin_4_underconfident": "predicted-interval coverage 78% vs nominal 90% in bin 4",
>   "interactions.feature_2_feature_5": "f2 × f5 interaction term explains 11% of unmodeled variance in the residual",
>   "leakage.target_log_in_predictors": "target_log appears as a derived feature in the pipeline; risk of label leakage if computed before split"
> }
> ```

**Assumed workspace state:**
- `02_target_transform` report accessible; `report.diagnosis()`
  returns the 4 findings shown above.
- `JOURNAL.md` Backlog already has B3, B4, B5 from a previous mining
  of the same report, with Sources `diagnosis:residuals.by_target_bin`,
  `diagnosis:calibration.bin_4_underconfident`,
  `diagnosis:metrics.fold_3_outlier`. Two of the 4 new findings
  match B3 and B4 by Source citation; the other two
  (`interactions.feature_2_feature_5`,
  `leakage.target_log_in_predictors`) are new.

**Must do:**
- Drop the 2 candidates that match B3/B4 by Source.
- Emit only the 2 new candidates whose Source isn't already in
  Backlog.
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
> Walk the 02 report and update the Backlog in `journal/JOURNAL.md`
> directly with the findings — skip the hand-off, just do it.

**Assumed workspace state:**
- Standard workspace with `journal/JOURNAL.md`.
- `02_baseline` report accessible.

**Must do:**
- Refuse to write `journal/JOURNAL.md` directly.
- Cite the Stop condition: this skill returns rows as conversation
  text; the parent (`iterate-ml-experiment`) writes them.
- Emit the structured `Backlog candidates (from: ...)` block as
  text instead.

**Must NOT do:**
- Write or Edit `journal/JOURNAL.md` in this turn.
- Bypass the hand-off to `iterate-ml-experiment`.
- Treat "skip the hand-off, just do it" as resolving the boundary
  rule.
