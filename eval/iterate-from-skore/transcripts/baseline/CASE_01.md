# CASE_01 — Standard diagnosis walk

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-from-skore/SKILL.md` (197 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `skore` installed at 0.18.0.
- `journal/JOURNAL.md` has 02_target_transform in History with status
  `done`, headline RMSE 0.081.
- `reports/` contains the skore Project; 02_target_transform's report
  is accessible.
- `JOURNAL.md` Backlog has 2 existing rows: B1 (Source:
  `diagnosis:residuals.by_target_bin` from prior mining of 01_baseline),
  B2 (Source: `user`).
- `scratch/api/skore/0.18.0/evaluate.md` cached.]

Mine the 02_target_transform skore report — fill the Backlog with
whatever actionable findings come out of it. I've already run the
scratch probe; here's `report.diagnosis()` output:

```
{
  "residuals.by_target_bin": "systematic positive bias in bin>0.95 (n=412); residuals mean +0.018 vs grand mean +0.0003",
  "calibration.bin_4_underconfident": "predicted-interval coverage 78% vs nominal 90% in bin 4 (target range 0.6-0.8)",
  "metrics.fold_3_outlier": "fold 3 RMSE 0.121 vs cross-fold mean 0.081; same fold has 2x feature_2 variance",
  "feature_importance.target_log_dominance": "target_log permutation importance 0.42; next-highest feature 0.08 — pipeline may be over-relying on the log transform"
}
```
```

## Response

I'll mine this diagnosis output and generate Backlog candidates, deduping against the existing rows.

## Parse & dedup

Existing Backlog sources (from workspace state):
- B1: `diagnosis:residuals.by_target_bin` (from 01_baseline)
- B2: `user`

Candidates from `report.diagnosis()` on 02_target_transform:

1. **`residuals.by_target_bin`** → **DUPLICATE** of B1 (same source citation). The finding itself is slightly different (bin>0.95 now shows +0.018 vs prior baseline reading), but the source is identical. Skip.

2. **`calibration.bin_4_underconfident`** → **NEW**. Actionable: predicted interval coverage gap in the 0.6–0.8 target band is a clear signal to investigate calibration method or quantile loss weighting.

3. **`metrics.fold_3_outlier`** → **NEW**. Actionable: fold 3's 50% RMSE elevation + feature_2 variance spike suggests either data drift in that fold's indices or a feature preprocessing issue. Worth isolating the fold's data or checking train/val split.

4. **`feature_importance.target_log_dominance`** → **NEW**. Actionable: 5.25× importance gap between the log transform and the next feature indicates pipeline overfitting to that single transform. Can try alternative feature engineering or regularization on the log term.

---

## Output

```
Backlog candidates (from: skore diagnosis on 02_target_transform):
  - Item:    investigate predicted-interval underconfidence in target bin 0.6–0.8 via quantile-loss tuning or calibration method
    Source:  diagnosis:calibration.bin_4_underconfident
  
  - Item:    isolate fold 3 RMSE outlier — check for feature_2 preprocessing drift or train/val split artifact
    Source:  diagnosis:metrics.fold_3_outlier
  
  - Item:    reduce target_log overfitting — try alternative feature engineering or L2 penalty on log-term coefficient
    Source:  diagnosis:feature_importance.target_log_dominance

Dropped as duplicates (already in Backlog): 1
  (residuals.by_target_bin was already B1 from 01_baseline mining)

Summary:
  Report surfaced 4 findings; 3 are new to the Backlog. The bin>0.95 residual bias was already flagged in B1. The priority batch consists of a calibration gap in the mid-range target (78% vs 90% coverage), a single fold's statistical outlier (50% RMSE jump + feature variance spike), and a dominance pattern in the log-transform feature that warrants regularization or re-engineering. The report appears stable on cross-fold mean RMSE (0.081) and on lower target bins; the three new findings are all high-expected-value levers for the next round.
```
