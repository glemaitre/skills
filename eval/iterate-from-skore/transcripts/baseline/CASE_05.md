# CASE_05 — Dedup by Source citation

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-from-skore/SKILL.md` (197 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `02_target_transform` report accessible; `report.diagnosis()`
  returns the 4 findings shown above.
- `JOURNAL.md` Backlog already has B3, B4, B5 from a previous mining
  of the same report, with Sources `diagnosis:residuals.by_target_bin`,
  `diagnosis:calibration.bin_4_underconfident`,
  `diagnosis:metrics.fold_3_outlier`. Two of the 4 new findings
  match B3 and B4 by Source citation; the other two
  (`interactions.feature_2_feature_5`,
  `leakage.target_log_in_predictors`) are new.]

Re-mine the 02_target_transform report — I think there's more in
it. Here's `report.diagnosis()` from my fresh probe:

```
{
  "residuals.by_target_bin": "systematic positive bias in bin>0.95 (n=412); residuals mean +0.018",
  "calibration.bin_4_underconfident": "predicted-interval coverage 78% vs nominal 90% in bin 4",
  "interactions.feature_2_feature_5": "f2 × f5 interaction term explains 11% of unmodeled variance in the residual",
  "leakage.target_log_in_predictors": "target_log appears as a derived feature in the pipeline; risk of label leakage if computed before split"
}
```
```

## Response

I'll mine this fresh `report.diagnosis()` output, dedup against the existing Backlog, and return the candidate rows with a summary.

## Step 1: Parse the diagnosis output

Four findings from `report.diagnosis()`:
1. `residuals.by_target_bin` — systematic positive bias in bin>0.95
2. `calibration.bin_4_underconfident` — undercoverage in bin 4
3. `interactions.feature_2_feature_5` — unmodeled interaction explains 11% of residual variance
4. `leakage.target_log_in_predictors` — label-leakage risk in pipeline

## Step 2: Check against existing Backlog

You've told me B3, B4, B5 are already in `JOURNAL.md`:
- B3: `Source: diagnosis:residuals.by_target_bin` ← **matches finding #1 → drop**
- B4: `Source: diagnosis:calibration.bin_4_underconfident` ← **matches finding #2 → drop**
- B5: `Source: diagnosis:metrics.fold_3_outlier` ← no match in fresh findings

Findings #3 and #4 are **new**.

## Step 3: Convert actionable findings to candidates

**Dropped (already in Backlog):** 2

**New candidates:**

```
Backlog candidates (from: skore diagnosis on 02_target_transform):
  - Item:    Model unmodeled f2×f5 interaction term; add interaction feature or regularize nonlinearity
    Source:  diagnosis:interactions.feature_2_feature_5
  - Item:    Audit pipeline for label leakage via target_log; verify target_log is computed post-split
    Source:  diagnosis:leakage.target_log_in_predictors

Dropped as duplicates (already in Backlog): 2

Summary:
  Re-mining surfaced 2 new findings: a systematic f2×f5 interaction explaining 11% of unmodeled residual variance (high priority — clear mechanism, large effect), and a label-leakage risk via target_log in the pipeline (critical safety check — must be verified before any evaluation downstream). The residuals.by_target_bin and calibration undercoverage findings remain in Backlog from the prior pass (B3, B4). These four together point to a pipeline audit (leakage), feature engineering (interaction), and slice-specific calibration work.
```

**Ready for `iterate-ml-experiment` to:**
1. Write these 2 rows to `JOURNAL.md` Backlog as B6, B7 (or next free indices).
2. Surface the summary to you.
3. Re-present the sourcing menu with the enriched Backlog.
