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
    is_active: bool | None = None
    user_type: str | None = None


class ProviderListParams(BaseModel):
    """Query parameters for the providers list endpoint."""

    client: str | None = None
    client_in: str | None = None
    email: str | None = None
    first_name: str | None = None
    id_in: str | None = None
    is_active: bool | None = None
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
    primary_practice_location: str | None = None
    client: str | None = None
    org_joining_date: date | None = None
    cc_emails: list[str] | None = None


class ProviderCAQHImport(BaseModel):
    """Payload for importing a provider via CAQH.

    Per the spec, ``email``, ``caqh_username`` and ``caqh_password`` are
    required; ``first_name`` and ``last_name`` are optional.
    """

    email: str
    caqh_username: str
    caqh_password: str
    first_name: str | None = None
    last_name: str | None = None
    provider_practice_locations: list[str] | None = None
    primary_practice_location: str | None = None


class ProviderCreate(BaseModel):
    """Payload for creating a provider without CAQH.

    Per the spec, only ``email``, ``first_name`` and ``last_name`` are
    required; ``client``, ``document_url`` and ``document_type`` are now
    optional.
    """

    email: str
    first_name: str
    last_name: str
    client: str | None = None
    document_url: str | None = None
    document_type: str | None = None
    provider_practice_locations: list[str] | None = None
    primary_practice_location: str | None = None
    org_joining_date: date | None = None


class ProviderCreateResponse(BaseModel):
    """Response returned when creating a provider.

    ``source_of_joining`` is one of: ``FROM_INVITE``,
    ``FROM_BULK_PROVIDERS_EXCEL_IMPORT``, ``FROM_SINGLE_PROVIDER_IMPORT``,
    ``FROM_MIGRATION_SCRIPTS``, ``PROVIDER_CREATE_API``,
    ``SINGLE_USER_ADDED_FROM_BACKEND``.
    """

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    provider_practice_locations: list[str] | None = None
    primary_practice_location: str | None = None
    client: str | None = None
    document_url: str | None = None
    document_type: str | None = None
    source_of_joining: str | None = None


class CaqhImportRequest(BaseModel):
    """A CAQH import request record."""

    id: int | None = None
    caqh_username: str | None = None
    caqh_password: str | None = None
    full_name: str | None = None
    signature: str | None = None


class CaqhImportRequestCreate(BaseModel):
    """Payload for requesting a CAQH import."""

    caqh_username: str
    caqh_password: str
    full_name: str
    signature: str


class CaqhImportRequestListParams(BaseModel):
    """Query parameters for the CAQH import requests list endpoint."""

    limit: int | None = None
    offset: int | None = None
    provider: str | None = None


class ProviderOrgJoiningDate(BaseModel):
    """A provider's organization joining date."""

    id: str | None = None
    org_joining_date: date | None = None


class PracticeLocationProvidersCreate(BaseModel):
    """Payload for associating providers with a practice location."""

    providers: list[str]
    practice_location: str
