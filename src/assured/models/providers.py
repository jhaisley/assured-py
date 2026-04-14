"""Provider models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class Provider(BaseModel):
    """A provider account."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    npi: str | None = None
    full_name: str | None = None
    provider_profile_id: str | None = None
    profile_completeness_percentage: float | None = None


class ProviderListParams(BaseModel):
    """Query parameters for the providers list endpoint."""

    email: str | None = None
    first_name: str | None = None
    id_in: str | None = None
    last_name: str | None = None
    limit: int | None = None
    npi: str | None = None
    offset: int | None = None
    ordering: str | None = None
    profile_completeness: bool | None = None
    search: str | None = None


class ProviderInvite(BaseModel):
    """Payload for inviting a provider."""

    email: str
    first_name: str
    last_name: str
    provider_practice_locations: list[str] | None = None
    client: str | None = None
    org_joining_date: date | None = None


class ProviderCAQHImport(BaseModel):
    """Payload for importing a provider via CAQH."""

    email: str
    first_name: str
    last_name: str
    caqh_username: str
    caqh_password: str
    provider_practice_locations: list[str] | None = None


class ProviderCreate(BaseModel):
    """Payload for creating a provider without CAQH."""

    email: str
    first_name: str
    last_name: str
    provider_practice_locations: list[str] | None = None
    client: str | None = None
    org_joining_date: date | None = None
    document_url: str | None = None
    document_type: str | None = None
