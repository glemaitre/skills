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
# Only vs TARGET. If there are more than 12 other columns, keep the
# ones most associated with the target (numeric Pearson) or the first
# 12. Do not pairplot the whole frame.

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
for name in bivariate_cols:
    if not pd.api.types.is_numeric_dtype(FRAME[name]):
        continue
    g = sns.relplot(data=FRAME, x=name, y=TARGET, alpha=0.4)
    g.savefig(OUT / f"bivariate_{name}.png", bbox_inches="tight")
    g

# %% [markdown]
# ## Leakage candidates
#
# Flags only — not a train/test split. Splitter choice is a later gate.

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
