# When to use which plotting API

First match in `SKILL.md` wins. One-liners, not a gallery.

## Owned (do not reimplement)

skore report accessors and sklearn `*Display` objects (confusion
matrix, ROC, calibration, residual). Evaluate and audit own those.

## Plotly Express

Interactive (hover, zoom, pan). Write a sibling HTML file, not a PNG.

```python
fig = px.scatter(df, x="a", y="b", hover_data=["id"])
fig.write_html(OUT / "interactive_scatter.html", include_plotlyjs=True)
```

Caller markdown (implications; glance stays TableReport-only
when the caller is explore):

```html
<iframe src="interactive_scatter.html" width="100%" height="640"></iframe>
```

Do not overwrite `data_analysis_<table>.html`. Do not use a CDN.

## seaborn

Tidy pandas. Statistical or faceted. Prefer figure-level in
notebooks so the grid is the cell output.

```python
g = sns.displot(data=df, x="age", hue="target")
g.savefig(OUT / "age_hist.png", bbox_inches="tight")
g
```

```python
g = sns.catplot(data=df, x="target", y="income", kind="box")
g.savefig(OUT / "income_box.png", bbox_inches="tight")
g
```

```python
g = sns.relplot(data=df, x="a", y="b", hue="target", alpha=0.4)
g.savefig(OUT / "scatter.png", bbox_inches="tight")
g
```

Do not `import matplotlib.pyplot` for these. Do not `plt.close`.

## pandas `DataFrame.plot`

Simple bar / line / hist / area from a Series or a few columns.

```python
ax = counts.plot(kind="bar", title="class counts")
ax.figure.savefig(OUT / "class_counts.png", bbox_inches="tight")
ax.figure
```

## matplotlib

Custom layout, annotations seaborn hides, non-tidy geometry.
Notebook: `fig.savefig(path, bbox_inches="tight")` then `fig` as
the last expression. `plt.close(fig)` only in non-notebook
scripts.
