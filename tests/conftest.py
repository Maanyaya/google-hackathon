"""Pytest configuration — live LLM tests are opt-in."""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "live_llm: requires live Vertex AI / Gemini (set RUN_LIVE_TESTS=1)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.getenv("RUN_LIVE_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="Live LLM test — set RUN_LIVE_TESTS=1 to run")
    for item in items:
        if "live_llm" in item.keywords:
            item.add_marker(skip)
