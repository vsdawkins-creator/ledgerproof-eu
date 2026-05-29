"""Pytest fixtures — isolated DB per test."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    db = tmp_path / "state.db"
    monkeypatch.setenv("LPR_GTM_DB", str(db))
    monkeypatch.delenv("LPR_API_KEY", raising=False)
    monkeypatch.delenv("LPR_ENV", raising=False)
    return db
