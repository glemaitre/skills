# Folds

The fold count is an integer of at least 1, or `predefined`.

`1` is one train/test split drawn from a single table.

`2` or more is how often the model is retrained. On a time series
each fold is one refit on the history available at that moment.

`predefined` means the data already has a separate training table
and a test table. Offer it in this question only when the EDA
report, the text shipped with the data, or the user already names
those two tables. Quote that source. Do not offer it otherwise,
and do not invent the tables. If they choose it, write
`predefined`. Do not write `1` for that choice.

Do not name a splitter class, a gap argument, or a test-size
constructor. Horizon and gap are already recorded when the
deployment is time.
