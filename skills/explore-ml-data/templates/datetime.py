# %% [markdown]
# ## Datetime checks
#
# Light checks only — ADF / ACF / seasonal decomposition are extras.
# Include the relplot only when TARGET is numeric.

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
pd.DataFrame(datetime_summary)

# %%
long = FRAME.melt(
    id_vars=[TARGET],
    value_vars=datetime_cols,
    var_name="feature",
    value_name="when",
)
g = sns.relplot(
    data=long,
    x="when",
    y=TARGET,
    col="feature",
    alpha=0.3,
    facet_kws={"sharex": False},
)
g.savefig(OUT / "target_vs_datetime.png", bbox_inches="tight")
g
