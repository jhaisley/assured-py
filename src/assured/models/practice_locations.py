"""Practice location models."""

from __future__ import annotations

from pydantic import BaseModel


class PracticeLocation(BaseModel):
    id: str | None = None
    name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone: str | None = None
    fax: str | None = None
    npi: str | None = None
    tax_id: str | None = None


class PracticeLocationCreate(BaseModel):
    name: str
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    phone: str | None = None
    fax: str | None = None
    npi: str | None = None
    tax_id: str | None = None


class PracticeLocationListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    ordering: str | None = None
