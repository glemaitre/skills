<!--
Written from scratch/eda/<table>.json and the TableReport HTML.
Ground every claim in those artifacts. Modelling implications are
candidates, not decisions.
-->

# EDA — <project / dataset name>

_Generated from `eda/eda.py` on <YYYY-MM-DD>._

## Dataset at a glance

- **Tables:** <names / count>
- **Shape:** <rows> × <cols> (per table if several)
- **Target:** <column name + task: binary / multiclass / regression | none>

<iframe src="eda_<table>.html" width="100%" height="640"></iframe>

[Open the interactive report](eda_<table>.html)

## Modelling implications

Translate what the report shows into *candidate* modelling choices
(splitter, metric, leakage risk). The owning gates make the picks.
Put any saved figures next to the implication they support:
`![](eda/<name>.png)`.

## Open questions

Domain ambiguities for the user to confirm before modelling.
