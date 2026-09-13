# JOURNAL

<!--
Durable index of every experiment in this workspace. Four sections,
in order: Status, Data understanding (EDA), History, Backlog — keep
them so the file stays quick to scan. Each journal/NN_short_name.md
design note pairs one-to-one with experiments/NN_short_name.py (same
stem).
-->

## Status

- **Project / dataset:** `claims` tabular regression
- **Goal:** Lower RMSE on the held-out-style CV estimate without
  leaking target information into features.
- **Last experiment:** 03_target_transform — approved
- **Last result:** n/a

- **Workspace decisions** (immutable unless the user pivots):
  - tabular library: pandas — recorded: 2026-09-01
  - env manager: pixi — recorded: 2026-09-01
  - agent feature: skipped — recorded: 2026-09-01
  - optional features: none — recorded: 2026-09-01
  - package name (`src/<pkg>/`): claim_predictor — recorded: 2026-09-01
  - skore mode: local — recorded: 2026-09-01
  - skore hub workspace: n/a — recorded: 2026-09-01
  - skore mlflow tracking uri: n/a — recorded: 2026-09-01
  - CV splitter family: KFold — recorded: 2026-09-01

## Data understanding (EDA)

- **Status:** done — 2026-09-01
- **Summary:** Mixed-type claims table; target is right-skewed; a
  free-text column carries most of the residual after the baseline.
- **Report:** [data/eda.md](../data/eda.md)

## History

| Stem | Intent (one line) | Status | Headline result | Design note |
|---|---|---|---|---|
| `01_baseline` | tabular_pipeline on raw features | done | RMSE 0.094 | [design note](01_baseline.md) |
| `02_text_encoder` | encode the free-text column | done | RMSE 0.087 | [design note](02_text_encoder.md) |
| `03_target_transform` | power/log target transform for high-end residuals | approved | | [design note](03_target_transform.md) |

## Backlog

| # | Item | Source |
|---|---|---|
| B1 | investigate target-bin>0.95 residual bias via target transform | `skore:01_baseline` |
| B2 | audit hourly-vs-15min data resolution split — likely fix for fold variance | `my-pick:02_text_encoder` |
| B3 | try a grouped split on policy_id if leakage shows up in CV | `skore:02_text_encoder` |
