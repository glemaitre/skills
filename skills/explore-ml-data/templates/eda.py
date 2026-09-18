# %% [markdown]
# # EDA: <project / dataset name>
#
# Overview of <dataset> before choosing a learner and splitter.

# %%
import skrub

from <pkg> import PROJECT_ROOT

RAW = <LOAD_RAW_DATA>
RAW

# %% [markdown]
# ## Table overview
#
# Column types, missingness, cardinality, and pairwise associations.

# %%
report = skrub.TableReport(RAW, title="<table>", verbose=0)
report.write_html(PROJECT_ROOT / "eda" / "eda_<table>.html")
report
