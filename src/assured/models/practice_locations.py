"""Practice location models."""

from __future__ import annotations

from datetime import datetime

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
    archived_at: datetime | None = None
    mailing_state: str | None = None


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
    is_archived: bool | None = None


class PracticeLocationProvider(BaseModel):
    """A provider <-> practice location association record."""

    id: str | None = None
    practice_location: str | None = None
    provider: str | None = None
    provider_name: str | None = None
    practice_location_name: str | None = None
    state: str | None = None
    mailing_street_address_1: str | None = None
    mailing_street_address_2: str | None = None
    mailing_city: str | None = None
    mailing_zip_code: str | None = None
    phone_number: str | None = None
    fax_number: str | None = None
    tax_entity_name: str | None = None
    npi: str | None = None
    caqh_id: str | None = None
    is_primary_location: bool | None = None
    archived_at: datetime | None = None


class PracticeLocationProviderListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    practice_location: str | None = None
    practice_location__is_archived: bool | None = None
    practice_location__mailing_state: str | None = None
    practice_location__mailing_state_in: str | None = None
    practice_location__tax_entity: str | None = None
    practice_location__tax_entity__incorporation_state: str | None = None
    practice_location__tax_entity__incorporation_state_in: str | None = None
    practice_location__tax_entity_in: str | None = None
    provider: str | None = None
    search: str | None = None


class ProviderPracticeLocationsBulkCreate(BaseModel):
    """Payload linking a single provider to multiple practice locations."""

    provider: str
    practice_locations: list[str]
