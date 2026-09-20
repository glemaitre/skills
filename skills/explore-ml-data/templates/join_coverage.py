# %% [markdown]
# ## Join keys / coverage
#
# Diagnostic only. Do not write a joined frame. Do not treat the
# merge as the dataset. No TableReport on the join.

# %%
left = FRAME
right = FRAME_<OTHER_SLUG>
shared = sorted(left.columns.intersection(right.columns))
join_key_summary = pd.DataFrame(
    {
        "column": shared,
        "left_dtype": [str(left[c].dtype) for c in shared],
        "right_dtype": [str(right[c].dtype) for c in shared],
        "left_nunique": [int(left[c].nunique(dropna=False)) for c in shared],
        "right_nunique": [int(right[c].nunique(dropna=False)) for c in shared],
        "left_duplicated_key": [
            int(left[c].duplicated().sum()) for c in shared
        ],
        "right_duplicated_key": [
            int(right[c].duplicated().sum()) for c in shared
        ],
    }
)
join_key_summary

# %%
KEY = "<JOIN_KEY>"
left_key = left[KEY].dropna()
right_key = right[KEY].dropna()
left_set = set(left_key.tolist())
right_set = set(right_key.tolist())
join_coverage = pd.DataFrame(
    {
        "metric": [
            "left_rows",
            "right_rows",
            "left_only_keys",
            "right_only_keys",
            "shared_keys",
        ],
        "value": [
            len(left),
            len(right),
            len(left_set - right_set),
            len(right_set - left_set),
            len(left_set & right_set),
        ],
    }
)
join_coverage
