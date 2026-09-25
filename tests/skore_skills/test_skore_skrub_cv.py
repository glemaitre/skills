"""skore.evaluate + skrub DataOp CV interop (Pattern A vs Pattern B)."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import pytest
import skore
import skrub
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GroupKFold, KFold, TimeSeriesSplit

N_SPLITS = 2


def _frame(*, n: int = 20, n_groups: int = 4) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "x": list(range(n)),
            "y": [float(i % 5) for i in range(n)],
            "g": [f"g{i % n_groups}" for i in range(n)],
        }
    )


def _learner(
    *,
    mark_x: Callable[..., object],
) -> skrub.SkrubLearner:
    data = skrub.var("data")
    X = mark_x(data.drop(columns=["y", "g"]), data)
    y = data["y"].skb.mark_as_y()
    return X.skb.apply(DummyRegressor(), y=y).skb.make_learner()


def _iid_learner() -> skrub.SkrubLearner:
    return _learner(mark_x=lambda X, _data: X.skb.mark_as_X())


def _grouped_learner(*, cv: object | None) -> skrub.SkrubLearner:
    def mark_x(X: object, data: object) -> object:
        kwargs: dict = {"split_kwargs": {"groups": data["g"]}}
        if cv is not None:
            kwargs["cv"] = cv
        return X.skb.mark_as_X(**kwargs)

    return _learner(mark_x=mark_x)


def _is_cv_report(report: object) -> bool:
    return type(report).__name__ == "CrossValidationReport"


def _split_groups(
    report: object, frame: pd.DataFrame
) -> list[tuple[set[str], set[str]]]:
    """Train/test group ids per fold from the stored report."""
    splits = getattr(report, "_split_indices", None)
    if not splits:
        pytest.fail(f"cannot read fold indices from {type(report)!r}")
    out: list[tuple[set[str], set[str]]] = []
    for train_idx, test_idx in splits:
        out.append(
            (
                set(frame.loc[list(train_idx), "g"]),
                set(frame.loc[list(test_idx), "g"]),
            )
        )
    return out


def test_pattern_a_kfold_explicit_splitter() -> None:
    """Kwargs-free splitter: pass splitter=; DataOp has no cv / split_kwargs."""
    frame = _frame()
    report = skore.evaluate(
        _iid_learner(),
        data={"data": frame},
        splitter=KFold(n_splits=N_SPLITS),
    )
    assert _is_cv_report(report)


def test_pattern_a_time_series_split_explicit_splitter() -> None:
    """TimeSeriesSplit needs no split() kwargs — still Pattern A."""
    frame = _frame()
    report = skore.evaluate(
        _iid_learner(),
        data={"data": frame},
        splitter=TimeSeriesSplit(n_splits=N_SPLITS),
    )
    assert _is_cv_report(report)


def test_pattern_b_group_kfold_omit_splitter() -> None:
    """Groups live on the DataOp; evaluate must omit splitter=."""
    frame = _frame()
    report = skore.evaluate(
        _grouped_learner(cv=GroupKFold(n_splits=N_SPLITS)),
        data={"data": frame},
    )
    assert _is_cv_report(report)
    for train_g, test_g in _split_groups(report, frame):
        assert train_g.isdisjoint(test_g)


def test_trap_explicit_splitter_drops_groups() -> None:
    """splitter= on evaluate drops DataOp split_kwargs (groups becomes None)."""
    frame = _frame()
    with pytest.raises(ValueError, match="groups"):
        skore.evaluate(
            _grouped_learner(cv=GroupKFold(n_splits=N_SPLITS)),
            data={"data": frame},
            splitter=GroupKFold(n_splits=N_SPLITS),
        )


def test_trap_split_kwargs_requires_cv() -> None:
    """skrub 0.10 refuses split_kwargs without an explicit cv=."""
    with pytest.raises((TypeError, ValueError)):
        _grouped_learner(cv=None)


def test_trap_integer_cv_is_not_pattern_b() -> None:
    """cv=<int> plus groups is not Pattern B: skore cannot call .split on an int."""
    frame = _frame()
    learner = _grouped_learner(cv=N_SPLITS)
    with pytest.raises(AttributeError, match="split"):
        skore.evaluate(learner, data={"data": frame})
