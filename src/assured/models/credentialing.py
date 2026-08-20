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
    org_joining_date: str | None = None


class AssigneeDetails(BaseModel):
    """Nested assignee info in credentialing responses."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    suffix: str | None = None
    user_type: str | None = None
    is_active: bool | None = None


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


class CredentialingPacket(BaseModel):
    """A credentialing packet as returned by the packet endpoints.

    The spec documents ``CREDENTIALED`` as the only ``credentialing_status``
    value and ``CLEAR`` as the only ``packet_status`` value; both are kept as
    plain strings since production may return additional states.
    """

    id: str | None = None
    credentialing_request: str | None = None
    attestation_url: str | None = None
    credentialing_date: datetime | None = None
    recredentialing_date: datetime | None = None
    states: str | None = None
    credentialing_status: str | None = None
    packet_status: str | None = None
    provider: str | None = None


class CredentialingPacketListParams(BaseModel):
    """Query parameters for the credentialing packet list."""

    credentialing_request: str | None = None
    credentialing_status: str | None = None
    limit: int | None = None
    offset: int | None = None
    packet_status: str | None = None
    provider: str | None = None


class CredentialingNeedAction(BaseModel):
    """An item from the credentialing need-action list."""

    id: str | None = None
    assignee_details: AssigneeDetails | None = None
    provider_details: ProviderDetails | None = None
    state_codes: list[str] | None = None
    verification_event_tasks: list[dict] | None = None
    status: str | None = None
    created_at: datetime | None = None
    credentialing_type: str | None = None
    sla_days: int | None = None
    client_details: ClientDetails | None = None
    assigned_at: datetime | None = None
    requested_by_full_name: str | None = None


class CredentialingNeedActionListParams(CredentialingListParams):
    """Query parameters for the credentialing need-action list.

    Extends :class:`CredentialingListParams` with need-action-specific filters.
    """

    org_joining_date_after: str | None = None
    org_joining_date_before: str | None = None
    pending_verification_type_in: str | None = None
    recredentialing_date_after: str | None = None
    recredentialing_date_before: str | None = None


class MonitoringPacketEvent(BaseModel):
    """A monitoring packet event.

    ``result`` is one of ``CLEAR`` / ``CONCERN`` / ``MISSING_INFO``.
    """

    id: str | None = None
    type: str | None = None
    source: str | None = None
    result: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    acted_by_user: str | None = None
    psv_field: str | None = None
    psv_val: str | None = None
    oa_verified_at: datetime | None = None
    provider_details: ProviderDetails | None = None
    note: str | None = None
    monitoring_concern_notes: str | None = None


class MonitoringPacketEventListParams(BaseModel):
    """Query parameters for the monitoring packet events list."""

    acted_by: str | None = None
    admin_acknowledgement: str | None = None
    created_at_month: str | None = None
    credentialing_request: str | None = None
    credentialing_request__credentialing_type: str | None = None
    credentialing_request__provider: str | None = None
    credentialing_request__request_type: str | None = None
    credentialing_request__status: str | None = None
    credentialing_request__verifier_signed_off: bool | None = None
    id: str | None = None
    individual_npis: str | None = None
    limit: int | None = None
    oa_verified_at_after: datetime | None = None
    oa_verified_at_before: datetime | None = None
    offset: int | None = None
    ordering: str | None = None
    professional_id__professional_id_type: str | None = None
    professional_id__state: str | None = None
    result: str | None = None
    search: str | None = None
    type: str | None = None
    type_in: str | None = None


class OverviewLastRequest(BaseModel):
    """The last credentialing request summary in a provider credentialing overview."""

    id: str | None = None
    status: str | None = None
    request_completed_at: str | None = None
    state_codes: list[str] | None = None
    oa_completed_at: str | None = None
    packet_events_data: list[dict] | None = None
    attestation_url: str | None = None
    approver_name: str | None = None
    approval_date: str | None = None


class OverviewLastPacket(BaseModel):
    """The last credentialing packet summary in a provider credentialing overview."""

    id: str | None = None
    credentialing_date: str | None = None
    next_credentialing_date: str | None = None
    states: list[str] | None = None
    credentialing_status: str | None = None
    packet_status: str | None = None
    provider: str | None = None
    attestation_url: str | None = None


class ProviderCredentialingOverview(BaseModel):
    """Provider-level credentialing overview."""

    id: str | None = None
    email: str | None = None
    last_credentialing_request: OverviewLastRequest | None = None
    provider_type: str | None = None
    last_packet: OverviewLastPacket | None = None
    org_joining_date: str | None = None


class ProviderWithStates(BaseModel):
    """A provider eligible for credentialing, with selectable states."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    states_selector: list[str] | None = None


class ProviderWithStatesListParams(BaseModel):
    """Query parameters for the providers-for-credentialing-with-states list."""

    id_in: str | None = None
    limit: int | None = None
    offset: int | None = None
    search: str | None = None


class CloseRequestItem(BaseModel):
    """One credentialing request closure in a close-request payload.

    ``status`` only accepts ``CANCELLED``. ``reason`` accepts closure reason codes such as
    ``PROVIDER_WITHDRAWN_APPLICATION``, ``CLIENT_REQUESTED_CANCELLATION``, ``OUTREACH_EXHAUSTED``,
    ``DUPLICATE_CREDENTIALING_REQUEST``, ``OTHER``, etc. (see the API spec for the full list).
    """

    id: str
    status: str = "CANCELLED"
    approval_date: datetime | None = None
    approver_name: str | None = None
    closure_remarks: str | None = None
    request_closed_by: str | None = None
    reason: str | None = None
    notes: str | None = None


class ApprovalLetterSend(BaseModel):
    """Payload to send a credentialing approval letter to a provider."""

    client: str
    provider: str
    request: str
    additional_cc_emails: list[str] | None = None


class ApprovalLetterDetail(BaseModel):
    """Approval letter detail for a credentialing request."""

    cc_emails: list[str] | None = None
    recipient_email: str | None = None
    last_sent_date: datetime | None = None
    last_sent_status: str | None = None
    last_sent_id: str | None = None
    html_preview: str | None = None
    markdown_preview: str | None = None
