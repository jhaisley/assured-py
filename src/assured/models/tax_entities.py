"""Tax entity models."""

from __future__ import annotations

from pydantic import BaseModel


class TaxEntity(BaseModel):
    id: str | None = None
    name: str | None = None
    tax_id: str | None = None
    npi: str | None = None


class TaxEntityCreate(BaseModel):
    name: str
    tax_id: str | None = None
    npi: str | None = None


class TaxEntityListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    ordering: str | None = None
