"""Representations skore displays expose to notebooks and to the cell runner.

Audit cells leave a bare Display as the last expression. Editors render
``_repr_html_``; ``skore_skills cells run`` records ``__repr__``. These
tests pin both paths so ``audit-ml-pipeline`` does not have to snapshot
text by hand, and so a skore release that regresses either one fails
here instead of silently emptying an audit digest.
"""

from __future__ import annotations

import pandas as pd
import pytest
import skore
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import KFold

N_SPLITS = 2


@pytest.fixture(scope="module")
def report() -> object:
    """A cheap regression report carrying every display namespace."""
    frame = pd.DataFrame(
        {
            "x": list(range(30)),
            "z": [float(i % 7) for i in range(30)],
            "y": [float(i % 5) for i in range(30)],
        }
    )
    return skore.evaluate(
        DummyRegressor(),
        frame[["x", "z"]],
        frame["y"],
        splitter=KFold(n_splits=N_SPLITS),
    )


def _displays(report: object) -> dict[str, object]:
    return {
        "checks": report.checks.summarize(),
        "metrics": report.metrics.summarize(),
        "prediction_error": report.metrics.prediction_error(),
        "permutation_importance": report.inspection.permutation_importance(),
    }


@pytest.fixture(scope="module")
def displays(report: object) -> dict[str, object]:
    """Summary and plot displays reachable from the core audit cells."""
    return _displays(report)


@pytest.mark.parametrize(
    "name",
    ["checks", "metrics", "prediction_error", "permutation_importance"],
)
def test_display_repr_is_readable_text(displays: dict[str, object], name: str) -> None:
    """A bare Display digests as values, not ``<... object at 0x...>``."""
    text = repr(displays[name])
    assert " object at 0x" not in text
    assert len(text.splitlines()) > 1


@pytest.mark.parametrize(
    "name",
    ["checks", "metrics", "prediction_error", "permutation_importance"],
)
def test_display_renders_html_for_notebooks(
    displays: dict[str, object], name: str
) -> None:
    """The same bare Display carries the rich view an editor shows."""
    html = displays[name]._repr_html_()
    assert isinstance(html, str)
    assert html.lstrip().startswith("<")


def test_checks_repr_carries_codes_and_doc_urls(
    displays: dict[str, object],
) -> None:
    """``iterate-from-skore`` mines codes and mitigation links from the digest."""
    text = repr(displays["checks"])
    assert "issue(s)" in text
    assert "SKD" in text
    assert "docs.skore.probabl.ai" in text


def test_metrics_repr_carries_metric_values(displays: dict[str, object]) -> None:
    """Metric names and values reach the digest without ``.frame()``."""
    text = repr(displays["metrics"])
    assert "rmse" in text
    assert "mae" in text


def test_help_prints_the_display_tree(report: object, capsys) -> None:
    """``help()`` returns None and prints; the runner captures it as stdout."""
    assert report.metrics.help() is None
    printed = capsys.readouterr().out
    assert "Displays" in printed
    assert ".prediction_error" in printed


@pytest.mark.parametrize("namespace", ["metrics", "checks"])
def test_available_returns_a_list_of_names(report: object, namespace: str) -> None:
    """``available()`` returns names rather than printing them."""
    names = getattr(report, namespace).available()
    assert isinstance(names, list)
    assert names


@pytest.mark.parametrize("namespace", ["inspection", "data"])
def test_available_is_absent_on_some_namespaces(report: object, namespace: str) -> None:
    """Discovery must fall back to ``help()`` where ``available()`` is missing."""
    assert not hasattr(getattr(report, namespace), "available")
