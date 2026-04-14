"""Facility models."""

from __future__ import annotations

from pydantic import BaseModel


class FacilityProfile(BaseModel):
    id: str | None = None
    name: str | None = None
    facility_type: str | None = None
    status: str | None = None


class FacilityListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    ordering: str | None = None
