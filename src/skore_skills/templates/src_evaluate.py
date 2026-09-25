"""Optional Pattern A splitter object.

``skore.evaluate`` and ``project.put`` live in
``experiments/NN_*.py``, not here.

Pattern A (``KFold``, ``TimeSeriesSplit``, …): set ``splitter`` to a
real cross-validator and pass it as ``splitter=`` from the experiment
script. Do not pass this module's default ``None`` — that is an
80/20 holdout.

Pattern B (``GroupKFold`` / ``groups`` on the DataOp): do not import
or pass ``splitter`` at all. See
``evaluate-ml-pipeline/references/metadata-routing.md``.
"""

from __future__ import annotations

splitter = None
