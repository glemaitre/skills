# Search angles, corroboration, output

## Query angles

Fill from intake. Run 1, 3, and 5 first; add 2 and 4 if thin.

1. Practice: `EDA OR machine learning [domain] [concern] best practices`
2. Theory: `[concern] statistical [modality]`
3. Implementation: `how to [concern] Python pandas scikit-learn [domain]`
4. Academic: `[concern] [domain] survey OR benchmark 2023 2024 2025`
5. Pitfalls: `[concern] mistakes pitfalls leakage [domain]`

Queries must be distinct angles, not paraphrases of one string.

## Corroboration

| Claim | Minimum |
|---|---|
| Numeric threshold | 2 independent sources |
| Statistical test | 1 paper or textbook + 1 implementation doc |
| Domain rule | 1 domain survey or textbook; user still confirms |
| API / code pattern | Official docs only is enough |
| Sources disagree | State both; do not pick a side silently |

## Output template

```markdown
## Research: <concern in one line>

### Context
- Modality / domain: ...
- Target / model family: ... (or not yet specified)

### What is happening
Plain language, 2–4 sentences.

### Why it matters here
Consequence for this task, not a generic lecture.

### Ranked candidates
| Priority | Action | When | Trade-off |
|---|---|---|---|
| 1 | ... | ... | ... |

### Risks
- ...

### Confidence
HIGH | MEDIUM | LOW — one sentence why.

### Sources
Inline citations for every factual claim.
```

Optional code snippet: minimal, placeholders, does not write raw
files.
