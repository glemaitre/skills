# %% [markdown]
# ## Second-frame drift
#
# A second confirmed family that shares column names.
# Do not invent a holdout split. Disjoint schemas: omit this file.

# %%
OTHER = <OTHER_FRAME>
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
