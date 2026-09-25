# Comparison metric

One metric is the comparison. An imposed name, from a client or an
existing report, wins over a metric derived from the goal.

Otherwise the role follows the goal:

- a trustworthy probability or an interval uses a proper scoring
  rule (classification: Brier or log-loss; regression: a
  distributional score such as CRPS or log-score)
- ordering cases, without a threshold, uses a ranking metric such
  as AUC
- a point label uses a thresholded metric (precision, recall, F1,
  or a cost at that threshold)
- a point prediction uses a point-error metric (MAE or RMSE)

Record the role token and the metric name. Do not record a scorer
object or a constructor.
