# Extra analyses — append to `data_analysis/data_analysis.py`

Recipes, not a second notebook. Run this board only after the user
picks **Keep exploring** then **More extra analyses**. Do not ask
extras after the default pass. Then AskUserQuestion
`allow_multiple` (all unchecked). Only list items that apply and
were **not** already in the user prompt. Picks:
`add-python-package` for the extra lib (agent), append the matching
cells, `style`, re-run `cells run`, refresh `facts.py`, then write
`data_analysis.md`. PNG unless the user asked for hover. Load
`plot-ml-figure` if installed before figure cells. Save the PNG
and leave the figure visible; never `plt.close`.

Do not train/test split. Do not drop or rewrite raw rows.

## Multivariate / interactions

Lib: seaborn (already on the run path).

A few 2-way views among the bivariate column list, or
`sns.pairplot` on at most 6 numeric columns (target + top
associates). Save `interactions.png` and leave the pairplot
visible. Last expression: the grid (or the column list used).

## 2D projection (PCA)

Lib: scikit-learn. UMAP only if the user insists (`umap-learn`).

Numeric columns, median-impute in the cell for the plot only — do
not write an imputed table. `PCA(n_components=2)`, then
`sns.relplot` of the two components colored by target if set.
Save `pca.png` and leave the figure visible. Do not use PCA as a
model preprocessor here.

## Hypothesis tests

Lib: scipy.

| Feature | Target | Test |
|---|---|---|
| numeric | classification | ANOVA or Kruskal–Wallis via `scipy.stats` |
| categorical | classification | chi-square on a crosstab |
| numeric | regression | Spearman via `scipy.stats.spearmanr` |

Last expression: a small p-value table. Interpret as a signal, not
a modelling decision.

## Subgroup / segment

Ask which grouping column if the user did not name one.

`groupby(group)[TARGET]` summary (rate or mean). Optional facet
plot. Save `subgroup_<group>.png` when a figure helps.

## Full time-series

Only if a datetime column exists. Lib: statsmodels.

ADF on the target (if numeric) or on one numeric series;
ACF/PACF plots. Save `acf.png`. Additive seasonal decomposition
only when the series is regular. Last expression: ADF statistic
table.

## Domain-specific

Only if those dtypes exist. No extra lib unless needed.

- **Text** (object/string, high unique count): length describe,
  empty-string rate. Save `text_length.png` if useful.
- **Geo** (lat/lon-like names or values in range): min/max,
  out-of-range counts. Do not call a maps API.
