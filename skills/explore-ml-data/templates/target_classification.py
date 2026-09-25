# %% [markdown]
# ## Target distribution
#
# Class counts.

# %%
y = FRAME[TARGET]
counts = y.value_counts(dropna=False)
target_summary = counts.rename("count").to_frame()
target_summary["rate"] = target_summary["count"] / target_summary["count"].sum()
target_summary

# %%
plot_df = target_summary.reset_index(names=TARGET)
g = sns.catplot(data=plot_df, x=TARGET, y="count", kind="bar")
g.savefig(OUT / "target_distribution.png", bbox_inches="tight")
g

# %% [markdown]
# ## Feature vs target
#
# A readable subset of features versus the target, not every
# pairwise plot. Cap at 12 columns.

# %%
BIVARIATE_CAP = 12
bivariate_cols = [c for c in FRAME.columns if c != TARGET][:BIVARIATE_CAP]
pd.Series(bivariate_cols, name="bivariate_columns")

# %%
numeric_bivariate = [
    c for c in bivariate_cols if pd.api.types.is_numeric_dtype(FRAME[c])
]
long = FRAME.melt(
    id_vars=[TARGET],
    value_vars=numeric_bivariate,
    var_name="feature",
    value_name="value",
)
g = sns.catplot(
    data=long,
    x=TARGET,
    y="value",
    col="feature",
    col_wrap=4,
    kind="box",
    sharey=False,
)
g.savefig(OUT / "bivariate_grid.png", bbox_inches="tight")
g

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split.

# %%
leakage_flags: list[str] = []
if pd.api.types.is_numeric_dtype(y):
    corr = FRAME.select_dtypes("number").corrwith(y).abs().sort_values(ascending=False)
    for col, value in corr.items():
        if col == TARGET:
            continue
        if value is not None and value >= 0.99:
            leakage_flags.append(f"{col} abs(Pearson) vs {TARGET} = {value:.3f}")
for col in FRAME.columns:
    if col == TARGET:
        continue
    rates = FRAME.groupby(y, dropna=False)[col].apply(lambda s: s.isna().mean())
    if rates.max() - rates.min() >= 0.5:
        leakage_flags.append(f"{col} null rate differs by class: {rates.to_dict()}")
leakage_summary = pd.DataFrame({"flag": leakage_flags or ["none"]})
leakage_summary
