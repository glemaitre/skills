# Search angles, corroboration, output

Two modes. Survey proposes concerns from literature. Depth
ranks actions for one named concern.

## Survey

No named concern. Context from JOURNAL / dtypes / target /
domain is fine. Do **not** use EDA Open questions as queries
or as the concern list.

Run in parallel (distinct angles, not paraphrases). Bake in
domain and task when known:

1. Practice: `tabular machine learning [domain] [task] EDA best practices`
2. Pitfalls: `[domain] [task] leakage pitfalls common mistakes`
3. What to check: `what to check EDA [domain] tabular machine learning`

Add theory/papers only if that pass is thin. Fetch primary
pages.

Write `scratch/research/survey-<slug>.md`. **No** ranked
`measure` / `declare` action table.

```markdown
## Survey: <domain / task in one line>

### Context
- Stage: data_analysis | model
- Modality / domain: ...
- Target / model family: ... (or not yet specified)

### What is happening
Plain language, 2–4 sentences (literature landscape, not a
lecture on this table’s Open questions).

### Proposed concerns
| Concern | Why it may apply | Source |
|---|---|---|
| ... | ... | ... |

### Confidence
HIGH | MEDIUM | LOW — one sentence why.

### Sources
Inline citations for every factual claim.
```

Return the path. The caller asks which concerns to deepen.

## Depth

Need a specific concern. Run 1, 3, and 5 first; add 2 and 4
if thin.

1. Practice: `EDA OR machine learning [domain] [concern] best practices`
2. Theory: `[concern] statistical [modality]`
3. Implementation: `how to [concern] Python pandas scikit-learn [domain]`
4. Academic: `[concern] [domain] survey OR benchmark 2023 2024 2025`
5. Pitfalls: `[concern] mistakes pitfalls leakage [domain]`

Queries must be distinct angles, not paraphrases of one string.
If a domain is known, bake it into the queries.

## Corroboration

| Claim | Minimum |
|---|---|
| Numeric threshold | 2 independent sources |
| Statistical test | 1 paper or textbook + 1 implementation doc |
| Domain rule | 1 domain survey or textbook; user still confirms |
| API / code pattern | Official docs only is enough |
| Sources disagree | State both; do not pick a side silently |

## Lanes

Depth notes only. Every candidate row gets one lane. Callers
distill; do not guess.

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
