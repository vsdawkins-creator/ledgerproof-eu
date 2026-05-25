"""Shared pytest fixtures and configuration for the ledgerproof SDK test suite."""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-skip live tests when their env credentials aren't set.

    Tests marked ``@pytest.mark.live`` need ``LEDGERPROOF_LIVE_API_KEY`` to
    talk to api-eu prod. Without it, they're skipped rather than failed.
    """
    if os.environ.get("LEDGERPROOF_LIVE_API_KEY"):
        return
    skip = pytest.mark.skip(reason="set LEDGERPROOF_LIVE_API_KEY to run live tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
