"""Cheap pipeline HTML for Method: unfitted at construct, fitted after evaluate."""

from __future__ import annotations

import pandas as pd
import pytest
import skore
import skrub
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils import estimator_html_repr

N_SPLITS = 2


def _spy_fit(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []
    real = DummyRegressor.fit

    def spy(self: DummyRegressor, *args: object, **kwargs: object) -> DummyRegressor:
        calls.append(1)
        return real(self, *args, **kwargs)

    monkeypatch.setattr(DummyRegressor, "fit", spy)
    return calls


def test_unfitted_sklearn_pipeline_html_does_not_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """sklearn diagram HTML is structure-only; fit is never called."""
    calls = _spy_fit(monkeypatch)
    estimator = make_pipeline(StandardScaler(), DummyRegressor())
    html = estimator_html_repr(estimator)
    assert html.lstrip().startswith("<")
    assert "DummyRegressor" in html
    assert "--sklearn-color-unfitted-level-0" in html
    assert calls == []


def test_unfitted_skrub_learner_html_does_not_fit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SkrubLearner ``_repr_html_`` is the sklearn diagram, not ``report()``."""
    calls = _spy_fit(monkeypatch)
    learner = skrub.X().skb.apply(DummyRegressor(), y=skrub.y()).skb.make_learner()
    html = learner._repr_html_()
    assert html.lstrip().startswith("<")
    assert "DummyRegressor" in html
    assert "SkrubLearner" in html
    assert calls == []
    assert estimator_html_repr(learner).lstrip().startswith("<")


def test_fitted_skore_report_html_differs_from_unfitted() -> None:
    """After evaluate, overwrite Method HTML from a fitted fold, not ``estimator``."""
    frame = pd.DataFrame(
        {
            "x": list(range(20)),
            "y": [float(i % 5) for i in range(20)],
        }
    )
    learner = skrub.X().skb.apply(DummyRegressor(), y=skrub.y()).skb.make_learner()
    unfitted = estimator_html_repr(learner)
    report = skore.evaluate(
        learner,
        data={"X": frame[["x"]], "y": frame["y"]},
        splitter=KFold(n_splits=N_SPLITS),
    )
    fitted = estimator_html_repr(report.reports_[0].estimator_)
    assert unfitted != fitted
    assert "--sklearn-color-fitted-level-0" in fitted
    assert report.estimator is learner
