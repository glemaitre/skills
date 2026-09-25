# Validation

Either a cross-validation fold count or one train/test split.

`cv` records an integer fold count of at least 2. On a time series
that count is how often the model is retrained: each fold is one
refit on the history available at that moment.

`holdout` is one train/test split. The fold cell is then `n/a`.

Do not name a splitter class, a gap argument, or a test-size
constructor. Horizon and gap are already recorded when the
deployment is time.
