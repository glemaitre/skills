"""Agent-only snapshot. Copy to scratch/data_analysis/facts.py; do not commit.

Reuse the same load as data_analysis/data_analysis.py. Writes
TableReport.json (plot_distributions=False) and extras.json
(duplicates, target, correlations, leakage flags, png and html
paths).
"""

import json

import pandas as pd
import skrub

from <pkg> import PROJECT_ROOT

TARGET = <TARGET>  # column name str, or None
TASK = "<TASK>"  # classification | regression | none

RAW = <LOAD_RAW_DATA>
FRAME = RAW.to_pandas() if hasattr(RAW, "to_pandas") else RAW

html = PROJECT_ROOT / "data_analysis" / "data_analysis_<table>.html"
html.parent.mkdir(parents=True, exist_ok=True)
if not html.is_file():
    skrub.TableReport(RAW, title="<table>", verbose=0).write_html(html)

report = skrub.TableReport(
    RAW, title="<table>", verbose=0, plot_distributions=False
)
out = PROJECT_ROOT / "scratch" / "data_analysis"
out.mkdir(parents=True, exist_ok=True)
(out / "<table>.json").write_text(report.json(), encoding="utf-8")

n_dup = int(FRAME.duplicated().sum())
n_rows = int(len(FRAME))
analysis = PROJECT_ROOT / "data_analysis"
pngs = sorted(p.name for p in analysis.glob("*.png"))
htmls = sorted(
    p.name
    for p in analysis.glob("*.html")
    if p.name != "data_analysis_<table>.html" and not p.name.endswith(".nb.html")
)

extras: dict = {
    "n_rows": n_rows,
    "n_duplicate_rows": n_dup,
    "duplicate_rate": n_dup / n_rows if n_rows else 0.0,
    "target": TARGET,
    "task": TASK,
    "class_counts": None,
    "target_skew": None,
    "feature_target_corr": [],
    "leakage_flags": [],
    "pngs": pngs,
    "htmls": htmls,
}

if TARGET is not None and TARGET in FRAME.columns:
    y = FRAME[TARGET]
    if TASK == "classification":
        extras["class_counts"] = {
            str(k): int(v) for k, v in y.value_counts(dropna=False).items()
        }
    elif pd.api.types.is_numeric_dtype(y):
        extras["target_skew"] = float(y.skew())
    if pd.api.types.is_numeric_dtype(y):
        corr = (
            FRAME.select_dtypes("number")
            .corrwith(y)
            .abs()
            .sort_values(ascending=False)
        )
        extras["feature_target_corr"] = [
            {"column": col, "abs_pearson": float(val)}
            for col, val in corr.items()
            if col != TARGET and pd.notna(val)
        ][:20]
        extras["leakage_flags"] = [
            f"{row['column']} abs(Pearson) vs {TARGET} = {row['abs_pearson']:.3f}"
            for row in extras["feature_target_corr"]
            if row["abs_pearson"] >= 0.99
        ]
    if TASK == "classification":
        for col in FRAME.columns:
            if col == TARGET:
                continue
            rates = FRAME.groupby(y, dropna=False)[col].apply(lambda s: s.isna().mean())
            if rates.max() - rates.min() >= 0.5:
                extras["leakage_flags"].append(
                    f"{col} null rate differs by class: {rates.to_dict()}"
                )

(out / "extras.json").write_text(
    json.dumps(extras, default=str), encoding="utf-8"
)
