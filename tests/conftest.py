"""Shared test fixtures."""

from __future__ import annotations

import pytest
import respx

from assured.client import AssuredClient
from assured.settings import Settings


@pytest.fixture()
def settings() -> Settings:
    return Settings(base_url="https://test-api.example.com", api_key="test-key-123")


@pytest.fixture()
async def client(settings: Settings):
    """Provide a fully initialised AssuredClient backed by respx mocking."""
    async with AssuredClient(settings=settings) as c:
        yield c


@pytest.fixture()
def mock_api():
    """Activate respx route mocking for the test."""
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as rsps:
        yield rsps


# ---- Reusable response factories ----


def paginated_response(results: list[dict], *, count: int | None = None, next_url: str | None = None) -> dict:
    """Build a standard paginated API response dict."""
    return {
        "count": count if count is not None else len(results),
        "next": next_url,
        "previous": None,
        "results": results,
    }
