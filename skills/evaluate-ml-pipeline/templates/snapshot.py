"""Agent-only snapshot. Copy to scratch/results/<stem>/snapshot.py.

Do not commit. Re-open the stored report after ``put``. Do not call
``skore.evaluate`` or ``project.put``. Writes ``report.html``,
``report.txt``, ``locator.txt``, and fitted ``pipeline.html``.
Prefer ``_repr_html_`` on the fitted estimator. Do not call
``SkrubLearner.report`` or ``full_report``.
"""

import skore
from sklearn.utils import estimator_html_repr

from <pkg> import PROJECT_ROOT

STEM = "<stem>"
REPORT_ID = "<id>"
LOCATOR = "<REPORT_LOCATOR>"

# <SKORE_PROJECT_INIT>
project = skore.Project(
    name="<project-name>",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)

report = project.get(REPORT_ID)
results = PROJECT_ROOT / "scratch" / "results" / STEM
results.mkdir(parents=True, exist_ok=True)
(results / "report.html").write_text(report._repr_html_(), encoding="utf-8")
(results / "report.txt").write_text(repr(report) + "\n", encoding="utf-8")
(results / "locator.txt").write_text(LOCATOR + "\n", encoding="utf-8")

fitted = (
    report.estimator_
    if hasattr(report, "estimator_")
    else report.reports_[0].estimator_
)
render = getattr(fitted, "_repr_html_", None)
pipeline_html = render() if callable(render) else estimator_html_repr(fitted)
(results / "pipeline.html").write_text(pipeline_html, encoding="utf-8")
