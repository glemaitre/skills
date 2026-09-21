"""Custom metric routing across skore reports and skrub DataOps."""

from __future__ import annotations

import pandas as pd
import skore
import skrub
from sklearn.dummy import DummyRegressor
from sklearn.metrics import make_scorer, mean_absolute_error
from sklearn.model_selection import GroupKFold, KFold
from skore import Project

N_SPLITS = 2


def scaled_absolute_error(
    estimator: object,
    X: pd.DataFrame,
    y: pd.Series,
    *,
    scale: float,
) -> float:
    """Return a static-kwarg metric suitable for report persistence."""
    predictions = estimator.predict(X)
    return float(scale * mean_absolute_error(y, predictions))


def _frame(*, n: int = 20, n_groups: int = 4) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": list(range(n)),
            "sample_weight": [float(1 + i % 3) for i in range(n)],
            "y": [float(i % 5) for i in range(n)],
            "g": [f"g{i % n_groups}" for i in range(n)],
        }
    )


def _report_metric_frame(report: object) -> pd.DataFrame:
    return report.metrics.summarize(metric=["custom_mae", "scaled_mae"]).frame()


def test_report_metrics_survive_local_project_round_trip(tmp_path) -> None:
    frame = _frame()
    X = frame[["x"]]
    y = frame["y"]
    report = skore.evaluate(
        DummyRegressor(),
        X,
        y,
        splitter=KFold(n_splits=N_SPLITS),
    )

    report.metrics.add(
        make_scorer(mean_absolute_error, greater_is_better=False),
        name="custom_mae",
    )
    report.metrics.add(
        scaled_absolute_error,
        name="scaled_mae",
        scale=3.0,
        greater_is_better=False,
    )
    before = _report_metric_frame(report)

    assert set(before.index) == {"custom_mae", "scaled_mae"}
    assert before.loc["scaled_mae", "dummyregressor_mean"] == (
        3 * before.loc["custom_mae", "dummyregressor_mean"]
    )

    project = Project("custom-metrics", workspace=tmp_path)
    project.put("report", report)
    reloaded = project.get(report.id)
    pd.testing.assert_frame_equal(_report_metric_frame(reloaded), before)


def _dataop_learner(
    *,
    grouped: bool,
    weighted: bool,
) -> skrub.SkrubLearner:
    data = skrub.var("data")
    X_source = data.drop(columns=["y", "g"])
    if grouped:
        X_source = X_source.skb.mark_as_X(
            cv=GroupKFold(n_splits=N_SPLITS),
            split_kwargs={"groups": data["g"]},
        )
    else:
        X_source = X_source.skb.mark_as_X()

    sample_weight = X_source["sample_weight"]
    X = X_source.drop(columns=["sample_weight"])
    y = data["y"].skb.mark_as_y()
    predictions = X.skb.apply(DummyRegressor(), y=y)

    if weighted:
        scorer = make_scorer(mean_absolute_error, greater_is_better=False)
        predictions = predictions.skb.with_scoring(
            scorer,
            kwargs={"sample_weight": sample_weight},
            name="weighted_mae",
        )
    else:
        predictions = predictions.skb.with_scoring(
            "neg_mean_absolute_error",
            name="custom_mae",
        )
    return predictions.skb.make_learner()


def test_dataop_scoring_without_kwargs_uses_pattern_a() -> None:
    report = skore.evaluate(
        _dataop_learner(grouped=False, weighted=False),
        data={"data": _frame()},
        splitter=KFold(n_splits=N_SPLITS),
    )

    assert "custom_mae" in report.metrics.score().index


def test_weighted_dataop_scoring_survives_grouped_round_trip(
    tmp_path,
) -> None:
    frame = _frame()
    report = skore.evaluate(
        _dataop_learner(grouped=True, weighted=True),
        data={"data": frame},
    )
    before = report.metrics.score()

    assert "weighted_mae" in before.index
    for train_idx, test_idx in report._split_indices:
        train_groups = set(frame.loc[list(train_idx), "g"])
        test_groups = set(frame.loc[list(test_idx), "g"])
        assert train_groups.isdisjoint(test_groups)

    project = Project("weighted-dataop", workspace=tmp_path)
    project.put("report", report)
    reloaded = project.get(report.id)
    pd.testing.assert_frame_equal(reloaded.metrics.score(), before)
