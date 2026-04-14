"""Shared / generic model types."""

from __future__ import annotations

from pydantic import BaseModel


class PaginatedResponse[T](BaseModel):
    """Standard Assured paginated list envelope."""

    count: int = 0
    next: str | None = None
    previous: str | None = None
    results: list[T] = []


class ClientDetails(BaseModel):
    """Nested client info returned in several endpoints."""

    id: str | None = None
    name: str | None = None
    sop_file: str | None = None


class SignoffAllowed(BaseModel):
    """Credentialing sign-off permission check."""

    value: bool = False
    msg: str | None = None
