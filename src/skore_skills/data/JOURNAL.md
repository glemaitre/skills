# JOURNAL

<!--
Durable index of every experiment in this workspace. Four sections,
in order: Status, Data understanding, History, Backlog — keep them
so the file stays quick to scan. Each journal/NN_short_name.md
design note pairs one-to-one with experiments/NN_short_name.py (same
stem).
-->

## Status

| Variable | Value |
|---|---|
| Project / dataset | <fill in — e.g., `adult-census` classification> |
| Goal | <one sentence — what would "done" look like for this project?> |
| Last experiment | <NN_name> — <status: planned \| approved \| running \| done \| abandoned> |
| Last result | <one-line headline metric, or "n/a" if not yet run> |

## Data understanding

<!--
Short index entry — the full analysis lives in
data_analysis/data_analysis.md. If data exploration was skipped, keep
just the Status row as skipped.
-->

| Variable | Value |
|---|---|
| Status | <done \| skipped> — <YYYY-MM-DD> |
| Summary | <2–4 lines — dataset shape, target balance/skew, and the one or two findings that most shape the modelling choices. "n/a" until the data has been explored.> |
| Report | [data_analysis/data_analysis.md](../data_analysis/data_analysis.md) |

## History

<!--
One row per experiment, in chronological order. Newest at the bottom.
Status values: planned | approved | running | done | abandoned.
-->

| Stem | Intent (one line) | Status | Headline result | Report | Design note |
|---|---|---|---|---|---|
| <!-- e.g. `01_baseline` --> | <!-- "tabular_pipeline on raw features" --> | <!-- done --> | <!-- "ROC-AUC 0.86 ± 0.01" --> | <!-- [Open report](URL) · backend · id: ID; `n/a` while planned --> | <!-- [design note](01_baseline.md) --> |

## Backlog

<!--
Ideas not yet committed to a journal/NN_*.md design note. Each row
has a stable B<N> index so it can be picked by number ("go with B2").

Columns:
  - #      — stable index (B1, B2, ...); don't renumber on removal.
  - Item   — one-line description of the idea.
  - Source — where it came from, e.g. a finding from a prior
             experiment's report (`audit:<stem>:checks.<code>`), a
             synthesized idea (`my-pick:<stem>`), or a user request
             (`user`).

When an item becomes a design note, remove its row here and add the
experiment to History above.
-->

| # | Item | Source |
|---|---|---|
| <!-- B1 --> | <!-- "investigate target-bin>0.95 residual bias via target transform" --> | <!-- `audit:01_baseline:checks.SKD003` --> |
| <!-- B2 --> | <!-- "audit hourly-vs-15min data resolution split — likely fix for fold variance" --> | <!-- `my-pick:02_calendar_features` --> |
