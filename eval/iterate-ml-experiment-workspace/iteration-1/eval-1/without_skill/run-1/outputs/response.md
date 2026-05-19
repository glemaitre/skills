# What's Next: ML Experimentation Workflow

## Current State
Based on the workspace journal, the project has completed:
1. **01_baseline**: RMSE 0.094 (done)
2. **02_text_encoder**: RMSE 0.087 (done)

The backlog contains 3 candidate next experiments (B1, B2, B3) from previous `iterate-from-skore` analysis.

## Recommended Next Steps

### 1. **Review Backlog Candidates**
Before proceeding, clarify the context of the three backlog items (B1, B2, B3) from the skore report:
- Examine what insights and implications each candidate addresses
- Assess which addresses the highest-impact risk or opportunity
- Confirm that the proposed design aligns with project goals

### 2. **Design the Next Experiment**
Convert the selected backlog item into a formal design:
- Create a `journal/03_<name>.md` file with the experiment design
- Document the hypothesis: what specific improvement or validation are you targeting?
- Define success criteria: what RMSE or metric would constitute progress?
- Identify potential blockers or risks specific to this experiment

### 3. **Develop the Experiment Code**
- Create the corresponding `experiments/03_<name>.py` script
- Implement the feature engineering, modeling, or evaluation changes described in the design
- Ensure the script logs results in a format compatible with the project's evaluation pipeline

### 4. **Run and Validate**
- Execute the experiment in the workspace environment
- Compare results against the baseline (RMSE 0.094) and text encoder variant (RMSE 0.087)
- Document findings in the design note (Implications, Risks, Next Steps)

### 5. **Update Project Artifacts**
- Advance the journal's Status section: update "Last experiment" and "Last result"
- Move the completed experiment from Backlog to History table
- If new insights emerge, create additional backlog items (B4, B5, etc.)

## Key Questions to Answer First
1. What metric (RMSE, others?) is primary for this project?
2. What are the workspace decisions (env manager, tabular library, CV splitter, etc.)?
3. Do any of the three backlog items depend on shared infrastructure or have ordering constraints?

**Next action**: Review the backlog context and select which candidate to promote to the next formal experiment design.
