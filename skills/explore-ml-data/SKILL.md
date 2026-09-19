---
name: explore-ml-data
description: >
  Owns data understanding BEFORE any model is designed. Places
  `data_analysis/data_analysis.py` (TableReport plus duplicates,
  target, bivariate, leakage), runs `python -m skore_skills cells
  run`, dumps agent facts under `scratch/data_analysis/`, then
  writes `data_analysis/data_analysis.md` and JOURNAL § Data
  understanding. Never designs the model, never edits `src/<pkg>/`,
  never modifies raw data files.

  TRIGGER — any of:
  - The user asks to "explore the data", "do an EDA", "profile the
    dataset", "what does the data look like", "understand the data".
  - Triage sent the user here before modeling
    (`status.data_analysis` missing).
  - A new or changed data source needs (re-)understanding.
  - The user asks to add analysis to an already-recorded EDA
    (refresh: edit the `.py`, re-run, overwrite the `.md`).

  STOP when `python -m skore_skills status` shows no scaffold or no
  data: explain and send the user to setup or triage. Also stop when
  the request is not raw-data exploration, or when exploratory data
  analysis is already recorded and no refresh was requested.

  HOW TO USE: G-TABULAR then add pandas/polars + skrub + matplotlib
  + seaborn via `add-python-package`. Infer or ask the target.
  Copy `templates/data_analysis.py`, `cells run`, copy
  `templates/facts.py` to scratch, author `data_analysis.md`,
  then ask keep-exploring vs close. Resolve symbols via `api get`.
---

# Explore ML Data

One project-level exploratory data analysis: a notebook the user
can open, HTML reports, a short `data_analysis.md` that embeds
them, and a JOURNAL index row.

## Artifacts

| Path | Audience |
|---|---|
| raw data (anywhere) | User-owned, **read-only** |
| `data_analysis/data_analysis.py` | Human notebook — TableReport + ML-gap cells |
| `data_analysis/data_analysis_<table>.html` | Human — TableReport page, embedded from `data_analysis.md` |
| `data_analysis/*.png` | Human — figures for implications, never glance |
| `data_analysis/data_analysis.md` | Human + later modelling — TableReport iframes, implications |
| `scratch/data_analysis/<table>.json` | Agent — `TableReport.json()`; gitignored |
| `scratch/data_analysis/extras.json` | Agent — duplicates, target, leakage, png paths |
| JOURNAL § Data understanding | Index: status, 2–4 line summary, link |

TableReport owns dtypes, missingness, univariate distributions,
cardinality, and top pairwise associations. Extra cells cover
duplicates, target distribution, feature-vs-target, and leakage
candidates. Do not duplicate TableReport in extra cells.

Details: `references/cell_anatomy.md`. Extra recipes:
`references/extra_analyses.md`.

## Next-step pointers

| You came here for… | → next |
|---|---|
| Triage sent you here before modeling | → return findings; they inform the baseline |
| User free-text ("explore the data") | → surface findings; then keep-exploring vs close |
| Keep exploring | → extras, research, or free-text; no end-turn yet |
| Close this stage | → convert / site / git end-turn / `triage-ml-task` |
| Changed data source or "also plot X" | → overwrite `data_analysis/data_analysis.*`, refresh JOURNAL |

## Stop conditions

- **Read-only raw data.** Never clean, rewrite, or re-save the
  user's files. Cleaning belongs in `build-ml-pipeline`.
- **Deliverables under `data_analysis/`.** Raw load may point
  anywhere.
- **G-DATA-ANALYSIS run | skip.** AskUserQuestion. "Go fast" does
  not skip. Skip → JOURNAL Status row `skipped — <date>` and stop.
  Do not run `site build` on skip.
- **IPython on the run path.** Missing → `add-python-package` for
  `ipython` (`env route` agent). Decline → skip path. Do not
  `pixi add` / fabricate output.
- **G-TABULAR before `data_analysis/data_analysis.py`.**
  `status.policy.tabular`; else `choose-python-library` (recommend
  pandas) then `add-python-package` for that lib **and** `skrub`,
  `matplotlib`, and `seaborn`. No silent default. Do not install
  sklearn / skore / pytest unless the user picked an extra that
  needs them.
- **Target.** Infer from JOURNAL Status / the user prompt when the
  column is obvious. Otherwise AskUserQuestion (column names plus
  "no target yet"). Decline → `<TARGET>=None`, `<TASK>=none`;
  still run duplicates. Do not persist a policy key.
- **No train/test split.** Splitter choice is a later gate.
  Leakage cells are qualitative flags on the raw table.
- **`api get` this turn** for symbols used (cache hits count).
  `TableReport.json()` keys drift — `.get(...)`.
- **One `data_analysis/data_analysis.py`.** Repeat the TableReport
  cell per table. Re-run overwrites in place.
- **Do not design the model.** Implications in
  `data_analysis.md` only.
- Do not gitignore `data_analysis/`. Ignore specific raw patterns
  via `setup-git` if the user asks (default: don't).

## Pre-flight

```
- [ ] Detect: status.data_analysis present|skipped|missing
- [ ] G-DATA-ANALYSIS: run | skip (skip → JOURNAL only, STOP)
- [ ] G-TABULAR + add frame lib + skrub + matplotlib + seaborn
- [ ] Target: inferred | AskUserQuestion | none
- [ ] IPython available or add-python-package
- [ ] Place data_analysis/data_analysis.py from
      templates/data_analysis.py; cells run
- [ ] scratch/data_analysis/facts.py → <table>.json + extras.json
- [ ] Author data_analysis.md + JOURNAL
- [ ] AskUserQuestion keep exploring vs close (skip if user
      already closed the turn)
```

Tick, then run the matching step. Re-emit with evidence at end of turn.

## Procedure (run path)

1. Resolve `<TARGET>` / `<TASK>` (`classification` | `regression`
   | `none`). Copy `templates/data_analysis.py` →
   `data_analysis/data_analysis.py`. Substitute `<pkg>`,
   `<LOAD_RAW_DATA>`, `<table>`, `<TARGET>`, `<TASK>`,
   `<OTHER_FRAME>` (`None` unless a second table is already on
   disk). Keep the datetime block's output (empty frame is fine
   when no datetime columns). Markdown is about **this** analysis.
   `python -m skore_skills style` after the write.
2. `python -m skore_skills cells run
   data_analysis/data_analysis.py` — writes HTML and PNGs. A
   useless TableReport `repr` in the digest is expected.
3. Copy `templates/facts.py` → `scratch/data_analysis/facts.py`
   with the same load and target; run it; read
   `scratch/data_analysis/<table>.json` and `extras.json`.
4. Write `data_analysis/data_analysis.md` from
   `templates/data_analysis.md`: glance (one iframe per table and
   nothing else), modelling implications (include
   feature-engineering *candidates*), open questions. Reports
   and figures are embedded, not linked; `![](<name>.png)` sits
   beside the implication it supports, never in the glance.
   Ground claims in both JSON files and the HTML. Do not invent
   columns.
5. JOURNAL § Data understanding table: Status `done — <date>`,
   short summary (shape, target balance/skew, one or two findings
   that shape modelling), Report
   `[data_analysis/data_analysis.md](../data_analysis/data_analysis.md)`.
   Skip path: Status row only. Do not convert or `git end-turn` on
   skip.
6. **Keep exploring vs close** — unless the user already closed
   the turn (“EDA is done”, “close the turn”): **AskUserQuestion**
   one pick, **Close** preselected.

   - Keep exploring the data — no convert, no site build, no
     `git end-turn`. Then **AskUserQuestion** one pick: more extra
     analyses (`references/extra_analyses.md`); research this
     concern; I’ll describe what to plot. Research: load
     `research-ml-practice` if installed (ask the concern if the
     user did not name one); else one-line skip and stay on this
     menu. Do not invent literature. After extras or a confirmed
     plot, refresh facts/md. After research, copy confirmed
     candidates into implications / open questions even if the
     `.py` is unchanged. If research recommends a cell, append it
     only after the user confirms. Then re-ask keep vs close. Do
     not invent domain checklists.
   - Close this stage and pick the next action — End of turn
     below.

   If the original prompt already named extras (e.g. PCA), include
   those cells in step 1 and do not re-ask that extra.

Import failures → `add-python-package`, do not work around.

Refresh (already `done`, user asks for more plots): edit the
`.py`, re-run steps 2–5, then step 6. Do not re-ask
G-DATA-ANALYSIS.

## Dispatch

Called from `triage-ml-task` (explore-the-data intent, or
explore-first on a modeling request while `data_analysis` is
missing) and user free-text.

Calls: `add-python-package`, `api get`, `choose-python-library` /
stack for G-TABULAR, `research-ml-practice` if installed when the
user wants literature on a concern, `style` after
`data_analysis.py`.

Need a package? Load `add-python-package` if installed; else name
it and stop. Do not `env add` here.

## End of turn

Run this block **only after Close** (or when the user already
closed the turn). Keep exploring never reaches here.

If `policy.notebooks` is true, `export-ml-notebook` is installed,
run `python -m skore_skills notebook convert
data_analysis/data_analysis.py`, with `--html` when `policy.site`
is also true. Skip in one line otherwise. Missing jupytext /
nbclient / nbconvert → one-line skip naming `add-python-package`;
do not fail the turn, do not `pixi add`.

Then, if `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build` after durable files are on
disk. Skip in one line otherwise. Name a build error; do not fail
the data-analysis turn.

`python -m skore_skills git end-turn --stage data_analysis`. If
`invoke`, load `persist-ml-git`. Then load `triage-ml-task` if
installed. No `git commit`.
