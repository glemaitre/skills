"""Stay in-process unless a test is exercising composed-env re-exec."""

from __future__ import annotations

import pytest

from skore_skills.env import IN_DEV_ENV


@pytest.fixture(autouse=True)
def _skip_dev_reexec(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(IN_DEV_ENV, "1")
