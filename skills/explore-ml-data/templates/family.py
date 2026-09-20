# %% [markdown]
# ## Table overview: <OTHER_SLUG>
#
# A further confirmed family. Load shards in memory only.

# %%
RAW_<OTHER_SLUG> = <LOAD_OTHER>
FRAME_<OTHER_SLUG> = (
    RAW_<OTHER_SLUG>.to_pandas()
    if hasattr(RAW_<OTHER_SLUG>, "to_pandas")
    else RAW_<OTHER_SLUG>
)
RAW_<OTHER_SLUG>

# %%
report_<OTHER_SLUG> = skrub.TableReport(
    RAW_<OTHER_SLUG>, title="<OTHER_SLUG>", verbose=0
)
report_<OTHER_SLUG>.write_html(OUT / "data_analysis_<OTHER_SLUG>.html")
report_<OTHER_SLUG>

# %% [markdown]
# ## Duplicate rows: <OTHER_SLUG>
#
# Do not drop rows here — cleaning belongs in the pipeline.

# %%
n_dup_<OTHER_SLUG> = int(FRAME_<OTHER_SLUG>.duplicated().sum())
duplicate_summary_<OTHER_SLUG> = pd.DataFrame(
    {
        "n_rows": [len(FRAME_<OTHER_SLUG>)],
        "n_duplicate_rows": [n_dup_<OTHER_SLUG>],
        "duplicate_rate": [
            n_dup_<OTHER_SLUG> / len(FRAME_<OTHER_SLUG>)
            if len(FRAME_<OTHER_SLUG>)
            else 0.0
        ],
    }
)
duplicate_summary_<OTHER_SLUG>
