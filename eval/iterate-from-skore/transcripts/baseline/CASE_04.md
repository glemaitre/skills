# CASE_04 — Don't pick a winning finding

**Model:** `claude-haiku-4-5-20251001`  
**Label:** `baseline`  
**Skill:** `skills/iterate-from-skore/SKILL.md` (197 lines)

## Input (user message)

```
[Workspace state — read but do not narrate back:
- `04_grouped_cv` report accessible; `report.diagnosis()` returns 5
  actionable findings (shown above).
- `JOURNAL.md` Backlog has 1 row with Source `user` that wouldn't
  match any of the 5 new candidates' Source citations.]

The 04_grouped_cv report just landed. Mine it and tell me which
one I should run next. I've already run the probe; here's the
output:

```
{
  "residuals.by_group": "groups {17, 42, 88} have residual std 2.3x the cross-group mean — group-specific feature distributions diverge",
  "calibration.tail_underconfidence": "right-tail (target>0.92) coverage 71% vs nominal 90%",
  "metrics.group_3_outlier_fold": "fold containing group 88 has RMSE 0.18 vs 0.094 elsewhere",
  "feature_interactions.cross_group_signal": "feature_3 × group interaction explains 18% of grouped variance currently unmodeled",
  "splitter.train_test_size_imbalance": "GroupKFold yields fold-size range [42, 318]; smaller folds may need stratification or refit"
}
```
```

## Response

I'll mine the `04_grouped_cv` report and convert these findings into Backlog candidates.

Let me start by loading the report and walking its diagnostic surface programmatically.

```python
# scratch/2025-01-23_141500_skore_diagnosis.py
import sys
from pathlib import Path

# Locate the skore Project for this workspace
try:
    from skore import Project
except ImportError:
    print("ERROR: skore not importable — install via `pixi add skore` or check environment")
    sys.exit(1)

project_path = Path("reports")
if not project_path.exists():
    print(f"ERROR: skore Project store not found at {project_path}")
    sys.exit(1)

try:
    project = Project(project_path)
except Exception as e:
    print(f"ERROR: failed to open skore Project at {project_path}: {e}")
    sys.exit(1)

# List available reports
try:
    reports_list = project.list_items()
except Exception as e:
    print(f"ERROR: failed to list reports: {e}")
    sys.exit(1)

print(f"Available reports: {reports_list}")

# Locate the latest 04_grouped_cv report
cv_reports = [r for r in reports_list if "04_grouped_cv" in str(r)]
if not cv_reports:
    print("ERROR: no 04_grouped_cv report found in project")
    sys.exit(1)

latest_cv_key = cv_reports[-1]  # most recent by lexical sort
print(f"Using report: {latest_cv_key}")

try:
    report = project[latest_cv_key]
except Exception as e:
    print(f"ERROR: failed to load report {latest_cv_key}: {e}")
    sys.exit(1)

# Call report.diagnosis() to walk the diagnostic surface
try:
    diagnosis = report.diagnosis()
except AttributeError:
    print("ERROR: report.diagnosis() not available — skore version may not support v1 API")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: report.diagnosis() failed: {e}")
    sys.exit(1)

print("\n=== Diagnostic output (raw) ===")
print(diagnosis)
print("\n=== Diagnostic output (type) ===")
print(type(diagnosis))
if hasattr(diagnosis, '__dict__'):
    print(f"Keys: {diagnosis.__dict__.keys()}")
```

```bash
pixi run python scratch/2025-01-23_141500_skore_diagnosis.py
```

Now let me read the existing `JOURNAL.md` Backlog to check for duplicates:

```python
# scratch/2025-01-23_141501_check_backlog.py
from pathlib import Path
import re

journal_path = Path("JOURNAL.md")
if not journal_path.exists():
    print("No JOURNAL.md found")
else:
    content = journal_path.read_text()
    # Extract Backlog section
    match = re.search(r"## Backlog\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if match:
        backlog_text = match.group(1)
        print("=== Current Backlog ===")
        print(backlog_text)
        # Extract Source citations
        sources = re.findall(r"Source:\s+([^\n]+)", backlog_text)
        print(f"\nExisting Source citations: {sources}")
    else:
        print("No Backlog section found")
```

```bash
pixi run python scratch/2025-01-23_141501_check_backlog.py
```

Based on the diagnostic findings you've provided and the probe output, here are the **Backlog candidates**:

```
Backlog candidates (from: skore diagnosis on 04_grouped_cv):
  - Item:    Investigate group-specific residual inflation (groups 17, 42, 88) via feature engineering or group-conditional transforms
    Source:  diagnosis:residuals.by_group
  - Item:    Address right-tail (target>0.92) miscalibration (coverage 71% vs 90% nominal) via calibration adjustment or target-range-specific regularization
    Source:  diagnosis:calibration.tail_underconfidence
  - Item:    Isolate and mitigate group-88-driven fold performance outlier (RMSE 0.18 vs 0.094 baseline) via fold-stratification or group-aware resampling
    Source:  diagnosis:metrics.group_3_outlier_fold
  - Item:    Model feature_3 × group interaction (18% unexplained grouped variance) via explicit cross-group feature engineering or polynomial expansion
    Source:  diagnosis:feature_interactions.cross_group_signal
  - Item:    Rebalance GroupKFold fold sizes (range [42, 318]) via stratified resampling or fold-size-aware cross-validation strategy
    Source:  diagnosis:splitter.train_test_size_imbalance

Dropped as duplicates (already in Backlog): 0

Summary:
  The 04_grouped_cv diagnosis surfaced 5 actionable findings across residuals, calibration, metrics, interactions, and splitter design. Top payoff candidates are the group-specific residual inflation (2.3× the cross-group mean — clear mechanism, high signal) and the right-tail miscalibration (18% coverage gap — high-stakes region). The feature_3 × group interaction accounts for 18% of unmodeled grouped variance and is mechanistically tractable. The fold-size imbalance (42–318 range) and group-88 fold outlier are secondary but worth flagging; the imbalance may explain part of the outlier. No findings on metric stability or noise floor — the baseline is solid.
```

---

**Next steps:**

`iterate-ml-experiment` will now write these 5 rows into `JOURNAL.md` Backlog with `B1`–`B5` indices. You'll see the enriched Backlog and a sourcing menu. Pick a `B<N>` row to design the next experiment, or pick `user` if one of these findings prompts a different direction you want to explore first.
