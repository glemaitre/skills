# Prediction goal

What the comparison is about, before any model is chosen.

Classification has two goals. **Probabilities** means the score
should be a trustworthy probability. **Point labels** means the
decision at a threshold is what matters.

Regression has two goals. **Intervals** means the prediction should
carry a range or a distribution. **Point predictions** means a
single number per row is what matters.

Record one token: `probabilities`, `point_labels`, `intervals`, or
`point_predictions`. This does not choose an estimator or its
parameters.

`uncovered` means this menu does not fit the problem. Choosing it
leaves the closed menu. The next turn uses `references/fallback.md`.
