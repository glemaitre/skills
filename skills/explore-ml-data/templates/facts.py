"""Agent-only snapshot. Copy to scratch/data_analysis/facts.py; do not commit.

Reuse the same families and target as data_analysis/data_analysis.py.
Writes TableReport.json (plot_distributions=False) per family and
extras.json (tables[], target, correlations, leakage flags, png
and html paths).
"""

import json

import pandas as pd
import skrub

from <pkg> import PROJECT_ROOT

TARGET = <TARGET>  # column name str, or None
TASK = "<TASK>"  # classification | regression | none

# Confirmed families only — (slug, raw). First family holds TARGET.
FAMILIES = [
    ("<slug>", <LOAD_RAW_DATA>),
]

analysis = PROJECT_ROOT / "data_analysis"
analysis.mkdir(parents=True, exist_ok=True)
out = PROJECT_ROOT / "scratch" / "data_analysis"
out.mkdir(parents=True, exist_ok=True)

report_html_names: set[str] = set()
table_rows: list[dict] = []
target_frame = None

for slug, raw in FAMILIES:
    frame = raw.to_pandas() if hasattr(raw, "to_pandas") else raw
    html = analysis / f"data_analysis_{slug}.html"
    report_html_names.add(html.name)
    if not html.is_file():
        skrub.TableReport(raw, title=slug, verbose=0).write_html(html)
    report = skrub.TableReport(
        raw, title=slug, verbose=0, plot_distributions=False
    )
    (out / f"{slug}.json").write_text(report.json(), encoding="utf-8")
    n_dup = int(frame.duplicated().sum())
    n_rows = int(len(frame))
    has_target = TARGET is not None and TARGET in frame.columns
    table_rows.append(
        {
            "slug": slug,
            "n_rows": n_rows,
            "n_duplicate_rows": n_dup,
            "duplicate_rate": n_dup / n_rows if n_rows else 0.0,
            "has_target": has_target,
        }
    )
    if has_target and target_frame is None:
        target_frame = frame

if target_frame is None:
    _, raw0 = FAMILIES[0]
    target_frame = raw0.to_pandas() if hasattr(raw0, "to_pandas") else raw0

FRAME = target_frame

pngs = sorted(p.name for p in analysis.glob("*.png"))
htmls = sorted(
    p.name
    for p in analysis.glob("*.html")
    if p.name not in report_html_names and not p.name.endswith(".nb.html")
)

extras: dict = {
    "tables": table_rows,
    "n_rows": table_rows[0]["n_rows"] if table_rows else 0,
    "n_duplicate_rows": table_rows[0]["n_duplicate_rows"] if table_rows else 0,
    "duplicate_rate": table_rows[0]["duplicate_rate"] if table_rows else 0.0,
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
