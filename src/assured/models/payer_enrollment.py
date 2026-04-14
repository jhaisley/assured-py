"""Payer enrollment models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class GroupEnrollmentRequestCreate(BaseModel):
    """Payload for creating a group enrollment request."""

    health_plan: str | None = None
    practice_location: str | None = None
    tax_entity: str | None = None
    effective_date: str | None = None


class ProviderEnrollmentRequestCreate(BaseModel):
    """Payload for creating a provider enrollment request."""

    provider: str | None = None
    health_plan: str | None = None
    practice_location: str | None = None
    tax_entity: str | None = None
    effective_date: str | None = None


class ExistingProviderEnrollmentCreate(BaseModel):
    """Payload for adding an existing provider enrollment."""

    provider: str
    tax_entity: str
    state: str
    health_plan: str
    lobs: list[str]
    other_practice_locations: list[str] | None = None
    primary_practice_location: str
    par_status: str
    new_health_plan_id: str | None = None
    effective_date: str
    no_re_validation_date: bool | None = None
    re_validation_date: str | None = None
    no_proof_of_enrollment: bool | None = None
    proof_of_enrollments: str | None = None
    notes: str | None = None
    id: str | None = None


class ExistingProviderEnrollment(ExistingProviderEnrollmentCreate):
    """Response returned when an existing provider enrollment is created."""

    no_health_plan_id: bool | None = None
    welcome_letters: list[Any] | None = None
    contract_files: list[Any] | None = None
    fee_structures: list[Any] | None = None
    client: str | None = None


class HealthPlan(BaseModel):
    id: str | None = None
    name: str | None = None
    payer_name: str | None = None


class EnrollmentRequest(BaseModel):
    id: str | None = None
    status: str | None = None
    enrollment_type: str | None = None
    provider_name: str | None = None
    health_plan_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ActiveEnrollment(BaseModel):
    id: str | None = None
    provider_name: str | None = None
    health_plan_name: str | None = None
    status: str | None = None
    effective_date: str | None = None


class EnrollmentListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    ordering: str | None = None
    status: str | None = None


class ActiveEnrollmentListParams(BaseModel):
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    ordering: str | None = None
