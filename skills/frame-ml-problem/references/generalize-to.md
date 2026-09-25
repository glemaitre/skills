# Generalize to

**Generalize to** is the column whose ids will be new when the
model is used. Those ids must stay entirely out of the fit that is
scored. Name that column.

**Known at predict** lists columns that are present on a new row.
A group mean is only a baseline for one of those columns. The
generalize-to column is not known for a new id, so its mean is not
a baseline.

If there is no such column, write `n/a`. On an i.i.d. or time
deployment, generalize-to stays `n/a`.
