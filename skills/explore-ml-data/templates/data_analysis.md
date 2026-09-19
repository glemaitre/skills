<!--
Written from scratch/data_analysis/<table>.json,
scratch/data_analysis/extras.json, and the TableReport HTML.
Ground every claim in those artifacts. Modelling implications
are candidates, not decisions.
-->

# Exploratory data analysis — <project / dataset name>

_Generated from `data_analysis/data_analysis.py` on <YYYY-MM-DD>._

## Dataset at a glance

<!--
One embed per table and nothing else. The TableReport already
carries shape, dtypes, missingness, cardinality, and associations —
do not restate them as bullets, and do not put figures here.
-->

<iframe src="data_analysis_<table>.html" width="100%" height="640"></iframe>

## Modelling implications

Translate TableReport **and** extras (duplicates, target
balance/skew, feature-vs-target, leakage flags, any extra the user
picked) into *candidate* modelling choices (splitter, metric,
leakage risk). The owning gates make the picks.
Embed any saved figure next to the implication it supports —
`![<caption>](<name>.png)`, a sibling of this file, never a bare
link. Glance stays TableReport-only.

## Open questions

Domain ambiguities for the user to confirm before modelling
(why duplicates exist, whether a near-perfect correlate is leakage,
capped target, extra analyses they declined).
