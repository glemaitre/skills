# Search angles, corroboration, output

Two modes. Survey proposes extra **measurements** for a table
like this. Depth ranks actions for one named concern.

## Do not overfit the named table

Toy sets (`fetch_california_housing`, Adult, Titanic, …)
pollute search with sklearn/Kaggle *pipeline* tutorials.
Before any query, rewrite the problem as a **class** in the
scratchpad:

- Drop dataset / loader / file name from queries.
- “California housing, MedHouseVal” → “continuous
  housing-value regression, top-coded target, rounded lat/lon”.
- Already in the default notebook (TableReport, duplicates,
  univariate target, feature-vs-target, leakage flags) → do
  not re-propose.

Queries use **phenomena + domain + task + EDA extras**. Never
the proper name, `sklearn.datasets`, a Kaggle slug, or
“baseline pipeline / RandomForest / GridSearch”. Discard hits
whose payload is model fitting, sklearn `Pipeline`, or
leaderboard code unless they justify a **raw-table
measurement**. Stage `data_analysis` extras must be appendable
EDA cells (spatial autocorrelation of the target, cap/censor
share, occupancy outliers as flags) — not transformers or
learners.

JOURNAL and EDA findings are **context** for that rewrite.
They are not search strings and not the extras list unless a
fetched source supports them.

## Survey (EDA extra analyses)

Canned question from explore (or equivalent):

> Given the kind of problem in JOURNAL (domain, task,
> constraints) and the kinds of structure already seen in EDA
> (not the dataset’s proper name), what extra measurements on
> a raw table like this are still worth doing?

Loop (no Wolfram / maps / image gen; no Python plots here):

1. **Scratchpad** in the note: problem class (no dataset
   name); query type straightforward / breadth-first /
   depth-first; what JOURNAL + EDA already covered.
2. **Wide-net:** 2–4 parallel distinct-angle searches
   (practice, pitfalls, domain EDA extras). Bake the
   abstracted domain/task, not the table name. Example
   shapes:
   - `EDA extra analyses [domain] [task] raw table measurements`
   - `[phenomenon] exploratory analysis pitfalls leakage`
   - `what to measure before modeling [domain] [task] spatial OR censoring OR imbalance`
3. **Fetch** 3–5 primary pages (docs, papers, textbooks).
   Snippets are not enough. Drop tutorial-pipeline pages.
4. **Follow-up:** for each promising **measure** extra not
   already in the notebook, a subsequent targeted search if
   the first pass is thin or single-sourced. Still no
   dataset-name queries.
5. **Verification:** one-source claims stay uncertain or get
   a confirm search. Sources disagree → state both; do not
   pick a side silently.
6. **Completeness:** re-read the canned question. If the list
   is mostly `declare` / `evaluate`, search again for EDA
   measurements.

Write `scratch/research/survey-<slug>.md`. **No** ranked
pipeline action table.

```markdown
## Survey: extra measurements for <problem class>

### Plan
- Problem class: ... (no dataset name)
- Query type: straightforward | breadth-first | depth-first
- Already covered in EDA: ...

### Context
- Stage: data_analysis | model
- Modality / domain: ...
- Target / task: ... (or not yet specified)

### What is happening
Plain language, 2–4 sentences (literature on this *kind* of
table, not a sklearn dataset page).

### Proposed extras
| Extra | Lane | Why it may apply | Source |
|---|---|---|---|
| ... | measure \| declare \| evaluate \| confirm | ... | ... |

### Confidence
HIGH | MEDIUM | LOW — one sentence why.

### Sources
Inline citations for every factual claim.
```

Prefer **`measure`** rows for an EDA caller. Return the path.
The caller asks which extras to add.

## Depth

Need a specific concern. Same anti-overfit rewrite. A leakage
question may name a statistic on *this* frame; still do not
search the dataset’s sklearn page.

Run 1, 3, and 5 first; add 2 and 4 if thin.

1. Practice: `EDA OR machine learning [domain] [concern] best practices`
2. Theory: `[concern] statistical [modality]`
3. Implementation: `how to [concern] Python pandas scikit-learn [domain]`
4. Academic: `[concern] [domain] survey OR benchmark 2023 2024 2025`
5. Pitfalls: `[concern] mistakes pitfalls leakage [domain]`

Queries must be distinct angles, not paraphrases of one string.
Bake abstracted domain/task, not the table name.

Then fetch → verify → follow-up if thin → ranked lane table.

## Corroboration

| Claim | Minimum |
|---|---|
| Numeric threshold | 2 independent sources |
| Statistical test | 1 paper or textbook + 1 implementation doc |
| Domain rule | 1 domain survey or textbook; user still confirms |
| API / code pattern | Official docs only is enough |
| Sources disagree | State both; do not pick a side silently |

## Lanes

Every candidate / extra row gets one lane. Callers distill;
do not guess.

| Lane | Meaning |
|---|---|
| `measure` | Observation on the raw frame (plot, test, table) |
| `declare` | Pipeline structure (transform, encoder, join, leakage guard) |
| `evaluate` | Splitter, metric, calibration — not EDA cells, not fit |
| `confirm` | Domain or user judgment only |

## Depth output template

Write this file under `scratch/research/<slug>.md`. The caller
summarizes it; do not paste it wholesale into chat.

```markdown
## Research: <concern in one line>

### Plan
- Problem class: ... (no dataset name)
- Query type: straightforward | breadth-first | depth-first

### Context
- Stage: data_analysis | model
- Modality / domain: ...
- Target / model family: ... (or not yet specified)

### What is happening
Plain language, 2–4 sentences.

### Why it matters here
Consequence for this task, not a generic lecture.

### Ranked candidates
| Priority | Lane | Action | When | Trade-off |
|---|---|---|---|---|
| 1 | measure \| declare \| evaluate \| confirm | ... | ... | ... |

### Risks
- ...

### Confidence
HIGH | MEDIUM | LOW — one sentence why.

### Sources
Inline citations for every factual claim.
```

Optional code snippet: minimal, placeholders, does not write raw
files. Do not paste a matplotlib wall; callers write real cells
(and load `plot-ml-figure` if installed). Callers run `api get`
before real symbols.
