"""Agent-only snapshot. Copy to scratch/eda/facts.py; do not commit.

Reuse the same load as eda/eda.py. Writes TableReport.json for eda.md.
"""

import skrub

from <pkg> import PROJECT_ROOT

RAW = <LOAD_RAW_DATA>
report = skrub.TableReport(RAW, title="<table>", verbose=0)
html = PROJECT_ROOT / "eda" / "eda_<table>.html"
html.parent.mkdir(parents=True, exist_ok=True)
if not html.is_file():
    report.write_html(html)

out = PROJECT_ROOT / "scratch" / "eda"
out.mkdir(parents=True, exist_ok=True)
(out / "<table>.json").write_text(report.json(), encoding="utf-8")
