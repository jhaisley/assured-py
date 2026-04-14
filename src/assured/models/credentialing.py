"""Credentialing models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from assured.models.common import ClientDetails, SignoffAllowed


class ProviderDetails(BaseModel):
    """Nested provider info in credentialing responses."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    user_type: str | None = None
    is_active: bool | None = None
    provider_profile_id: str | None = None
    individual_npi: str | None = None
    provider_type: str | None = None


class CredentialingRequestCreate(BaseModel):
    """Payload to create a credentialing request."""

    provider: str
    credentialing_type: str = "INITIAL_CREDENTIALING"
    state_codes: list[str] | None = None


class CredentialingRequest(BaseModel):
    """A credentialing request as returned by the list endpoint."""

    id: str | None = None
    provider_details: ProviderDetails | None = None
    client_details: ClientDetails | None = None
    state_codes: list[str] | None = None
    assignee: str | None = None
    credentialing_type: str | None = None
    request_completed_at: datetime | None = None
    oa_completed_at: datetime | None = None
    automation_status: str | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    request_id: str | None = None
    attestation_url: str | None = None
    attestation_url_presigned: str | None = None
    request_type: str | None = None
    verifier_signed_off: bool | None = None
    is_signoff_allowed: SignoffAllowed | None = None
    assigned_at: datetime | None = None
    assignee_email: str | None = None
    assignee_full_name: str | None = None
    requested_by_full_name: str | None = None
    requested_by: str | None = None
    approval_date: str | None = None
    approver_name: str | None = None
    request_closed_by: str | None = None
    sla_days: int | None = None
    re_credentialing_date: str | None = None
    reason_for_termination: str | None = None


class CredentialingRequestDetail(CredentialingRequest):
    """Detailed credentialing request (same fields, returned by detail endpoint)."""


class CredentialingListParams(BaseModel):
    """Query parameters for the credentialing request list."""

    assigned_at_after: datetime | None = None
    assigned_at_before: datetime | None = None
    assignee: str | None = None
    assignee_in: str | None = None
    automation_status: str | None = None
    client_ids: str | None = None
    created_at_after: datetime | None = None
    created_at_before: datetime | None = None
    created_at_month: str | None = None
    credentialing_type: str | None = None
    individual_npis: str | None = None
    limit: int | None = None
    oa_completed_at_after: datetime | None = None
    oa_completed_at_before: datetime | None = None
    offset: int | None = None
    ordering: str | None = None
    provider: str | None = None
    provider_in: str | None = None
    provider_type: str | None = None
    request_completed_at_after: datetime | None = None
    request_completed_at_before: datetime | None = None
    request_type: str | None = None
    requested_by: str | None = None
    requested_by_in: str | None = None
    search: str | None = None
    state_codes_in: str | None = None
    status: str | None = None
    status_in: str | None = None
    tab: str | None = None
    updated_at_after: datetime | None = None
    updated_at_before: datetime | None = None
    verifier_signed_off: bool | None = None
