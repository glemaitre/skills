# %% [markdown]
# # Exploratory data analysis: <project / dataset name>
#
# Overview of <dataset> before choosing a learner and splitter.
# TableReport owns dtypes, missingness, univariate distributions,
# cardinality, and top pairwise associations — do not re-plot those.

# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import skrub

from <pkg> import PROJECT_ROOT

OUT = PROJECT_ROOT / "data_analysis"
OUT.mkdir(parents=True, exist_ok=True)

TARGET = <TARGET>  # column name str, or None
TASK = "<TASK>"  # classification | regression | none

RAW = <LOAD_RAW_DATA>
FRAME = RAW.to_pandas() if hasattr(RAW, "to_pandas") else RAW
RAW

# %% [markdown]
# ## Table overview
#
# Column types, missingness, cardinality, and pairwise associations.

# %%
report = skrub.TableReport(RAW, title="<table>", verbose=0)
report.write_html(OUT / "data_analysis_<table>.html")
report

# %% [markdown]
# ## Duplicate rows
#
# Exact duplicates inflate counts and can leak across a later split.
# Do not drop rows here — cleaning belongs in the pipeline.

# %%
n_dup = int(FRAME.duplicated().sum())
duplicate_summary = pd.DataFrame(
    {
        "n_rows": [len(FRAME)],
        "n_duplicate_rows": [n_dup],
        "duplicate_rate": [n_dup / len(FRAME) if len(FRAME) else 0.0],
    }
)
duplicate_summary

# %% [markdown]
# ## Target distribution
#
# Skip this cell block when TARGET is None.

# %%
if TARGET is None:
    target_summary = pd.DataFrame({"note": ["no target selected"]})
else:
    y = FRAME[TARGET]
    if TASK == "classification":
        counts = y.value_counts(dropna=False)
        target_summary = counts.rename("count").to_frame()
        target_summary["rate"] = target_summary["count"] / target_summary["count"].sum()
        fig, ax = plt.subplots()
        counts.plot(kind="bar", ax=ax)
        ax.set_title(f"{TARGET} class counts")
        fig.savefig(OUT / "target_distribution.png", bbox_inches="tight")
        plt.close(fig)
    else:
        target_summary = y.describe().to_frame(name=TARGET)
        target_summary.loc["skew"] = y.skew()
        fig, ax = plt.subplots()
        sns.histplot(y.dropna(), ax=ax)
        ax.set_title(f"{TARGET} distribution")
        fig.savefig(OUT / "target_distribution.png", bbox_inches="tight")
        plt.close(fig)
target_summary

# %% [markdown]
# ## Feature vs target
#
# Only vs TARGET. If there are more than 12 other columns, keep the
# ones most associated with the target (numeric Pearson) or the first
# 12. Do not pairplot the whole frame.

# %%
BIVARIATE_CAP = 12
bivariate_cols: list[str] = []
if TARGET is not None and TARGET in FRAME.columns:
    others = [c for c in FRAME.columns if c != TARGET]
    if len(others) > BIVARIATE_CAP and TASK != "none":
        numeric = FRAME[others].select_dtypes("number")
        if TASK == "regression" and pd.api.types.is_numeric_dtype(FRAME[TARGET]):
            ranked = numeric.corrwith(FRAME[TARGET]).abs().sort_values(ascending=False)
            bivariate_cols = [c for c in ranked.index if pd.notna(ranked[c])][
                :BIVARIATE_CAP
            ]
        else:
            bivariate_cols = others[:BIVARIATE_CAP]
    else:
        bivariate_cols = others[:BIVARIATE_CAP]
    for name in bivariate_cols:
        fig, ax = plt.subplots()
        if TASK == "classification" and pd.api.types.is_numeric_dtype(FRAME[name]):
            sns.boxplot(data=FRAME, x=TARGET, y=name, ax=ax)
        elif TASK == "regression" and pd.api.types.is_numeric_dtype(FRAME[name]):
            sns.scatterplot(data=FRAME, x=name, y=TARGET, ax=ax, alpha=0.4)
        else:
            plt.close(fig)
            continue
        ax.set_title(f"{name} vs {TARGET}")
        fig.savefig(OUT / f"bivariate_{name}.png", bbox_inches="tight")
        plt.close(fig)
pd.Series(bivariate_cols, name="bivariate_columns")

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split. Splitter choice is a later gate.

# %%
leakage_flags: list[str] = []
if TARGET is not None and TARGET in FRAME.columns:
    y = FRAME[TARGET]
    if pd.api.types.is_numeric_dtype(y):
        corr = FRAME.select_dtypes("number").corrwith(y).abs().sort_values(ascending=False)
        for col, value in corr.items():
            if col == TARGET:
                continue
            if value is not None and value >= 0.99:
                leakage_flags.append(f"{col} abs(Pearson) vs {TARGET} = {value:.3f}")
    if TASK == "classification":
        for col in FRAME.columns:
            if col == TARGET:
                continue
            rates = FRAME.groupby(y, dropna=False)[col].apply(lambda s: s.isna().mean())
            if rates.max() - rates.min() >= 0.5:
                leakage_flags.append(f"{col} null rate differs by class: {rates.to_dict()}")
leakage_summary = pd.DataFrame({"flag": leakage_flags or ["none"]})
leakage_summary

# %% [markdown]
# ## Datetime checks
#
# Include this block only when a datetime column exists. Light checks
# only — ADF / ACF / seasonal decomposition are extras (statsmodels).

# %%
datetime_cols = list(FRAME.select_dtypes(include=["datetime", "datetimetz"]).columns)
datetime_summary = []
for col in datetime_cols:
    series = FRAME[col]
    datetime_summary.append(
        {
            "column": col,
            "min": str(series.min()),
            "max": str(series.max()),
            "monotonic_increasing": bool(series.is_monotonic_increasing),
            "n_duplicate_timestamps": int(series.duplicated().sum()),
        }
    )
    if TARGET is not None and pd.api.types.is_numeric_dtype(FRAME[TARGET]):
        fig, ax = plt.subplots()
        ax.plot(series, FRAME[TARGET], ".", alpha=0.3)
        ax.set_title(f"{TARGET} vs {col}")
        fig.savefig(OUT / f"target_vs_{col}.png", bbox_inches="tight")
        plt.close(fig)
pd.DataFrame(datetime_summary)

# %% [markdown]
# ## Second-frame drift
#
# Include this block only when a second table is already on disk.
# Do not invent a holdout split.

# %%
OTHER = <OTHER_FRAME>  # DataFrame or None
if OTHER is None:
    drift_summary = pd.DataFrame({"note": ["no second frame"]})
else:
    other = OTHER.to_pandas() if hasattr(OTHER, "to_pandas") else OTHER
    rows = []
    for col in FRAME.columns.intersection(other.columns):
        left_null = float(FRAME[col].isna().mean())
        right_null = float(other[col].isna().mean())
        row = {"column": col, "null_rate": left_null, "other_null_rate": right_null}
        if pd.api.types.is_numeric_dtype(FRAME[col]) and pd.api.types.is_numeric_dtype(
            other[col]
        ):
            row["median"] = float(FRAME[col].median())
            row["other_median"] = float(other[col].median())
        rows.append(row)
    drift_summary = pd.DataFrame(rows)
drift_summary
