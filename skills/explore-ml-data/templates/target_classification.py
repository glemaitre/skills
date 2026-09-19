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
# Only vs TARGET. If there are more than 12 other columns, keep the
# first 12. Do not pairplot the whole frame.

# %%
BIVARIATE_CAP = 12
bivariate_cols = [c for c in FRAME.columns if c != TARGET][:BIVARIATE_CAP]
pd.Series(bivariate_cols, name="bivariate_columns")

# %%
for name in bivariate_cols:
    if not pd.api.types.is_numeric_dtype(FRAME[name]):
        continue
    g = sns.catplot(data=FRAME, x=TARGET, y=name, kind="box")
    g.savefig(OUT / f"bivariate_{name}.png", bbox_inches="tight")
    g

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split. Splitter choice is a later gate.

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
