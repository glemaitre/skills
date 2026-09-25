# %% [markdown]
# ## Target distribution
#
# Numeric target.

# %%
y = FRAME[TARGET]
target_summary = y.describe().to_frame(name=TARGET)
target_summary.loc["skew"] = y.skew()
target_summary

# %%
g = sns.displot(data=FRAME, x=TARGET)
g.savefig(OUT / "target_distribution.png", bbox_inches="tight")
g

# %% [markdown]
# ## Feature vs target
#
# A readable subset of features versus the target (numeric Pearson
# when many columns), not every pairwise plot. Cap at 12 columns.

# %%
BIVARIATE_CAP = 12
others = [c for c in FRAME.columns if c != TARGET]
numeric = FRAME[others].select_dtypes("number")
if len(others) > BIVARIATE_CAP and not numeric.empty:
    ranked = numeric.corrwith(FRAME[TARGET]).abs().sort_values(ascending=False)
    bivariate_cols = [c for c in ranked.index if pd.notna(ranked[c])][:BIVARIATE_CAP]
else:
    bivariate_cols = others[:BIVARIATE_CAP]
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
g = sns.relplot(
    data=long,
    x="value",
    y=TARGET,
    col="feature",
    col_wrap=4,
    alpha=0.4,
    facet_kws={"sharex": False},
)
g.savefig(OUT / "bivariate_grid.png", bbox_inches="tight")
g

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split.

# %%
leakage_flags: list[str] = []
corr = (
    FRAME.select_dtypes("number")
    .corrwith(FRAME[TARGET])
    .abs()
    .sort_values(ascending=False)
)
for col, value in corr.items():
    if col == TARGET:
        continue
    if value is not None and value >= 0.99:
        leakage_flags.append(f"{col} abs(Pearson) vs {TARGET} = {value:.3f}")
leakage_summary = pd.DataFrame({"flag": leakage_flags or ["none"]})
leakage_summary
