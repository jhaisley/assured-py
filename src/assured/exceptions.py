"""Custom exception hierarchy for Assured API errors."""

from __future__ import annotations

from typing import Any


class AssuredError(Exception):
    """Base exception for all Assured SDK errors."""


class AssuredAPIError(AssuredError):
    """Raised when the API returns a non-success HTTP status."""

    def __init__(self, status_code: int, detail: Any = None, *, url: str = "") -> None:
        self.status_code = status_code
        self.detail = detail
        self.url = url
        super().__init__(f"HTTP {status_code} from {url}: {detail}")


class AssuredAuthError(AssuredAPIError):
    """Raised on HTTP 401 — invalid or missing API key."""


class AssuredNotFoundError(AssuredAPIError):
    """Raised on HTTP 404 — resource not found."""


class AssuredValidationError(AssuredAPIError):
    """Raised on HTTP 400 — bad request / validation failure."""


class AssuredRateLimitError(AssuredAPIError):
    """Raised on HTTP 429 — rate limited (after retries exhausted)."""
