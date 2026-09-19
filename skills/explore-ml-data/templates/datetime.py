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
for col in datetime_cols:
    g = sns.relplot(data=FRAME, x=col, y=TARGET, alpha=0.3)
    g.savefig(OUT / f"target_vs_{col}.png", bbox_inches="tight")
    g
