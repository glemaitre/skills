"""Agent-only snapshot. Copy to scratch/data_analysis/facts.py; do not commit.

Reuse the same load as data_analysis/data_analysis.py. Writes
TableReport.json for data_analysis.md.
"""

import skrub

from <pkg> import PROJECT_ROOT

RAW = <LOAD_RAW_DATA>
report = skrub.TableReport(RAW, title="<table>", verbose=0)
html = PROJECT_ROOT / "data_analysis" / "data_analysis_<table>.html"
html.parent.mkdir(parents=True, exist_ok=True)
if not html.is_file():
    report.write_html(html)

out = PROJECT_ROOT / "scratch" / "data_analysis"
out.mkdir(parents=True, exist_ok=True)
(out / "<table>.json").write_text(report.json(), encoding="utf-8")
