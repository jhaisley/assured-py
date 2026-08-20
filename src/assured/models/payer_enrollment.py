"""Payer enrollment models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class GroupEnrollmentRequestCreate(BaseModel):
    """Payload for creating a group enrollment request.

    The spec marks ``tax_entity``, ``state``, ``health_plan``, ``lobs``, ``enroll_providers``,
    ``group_providers`` and ``primary_practice_location`` as required; they remain optional here
    for backward compatibility.

    Note:
        ``practice_location`` and ``effective_date`` are not part of the documented spec and are
        kept only for backward compatibility; prefer ``primary_practice_location``.
    """

    health_plan: str | None = None
    practice_location: str | None = None
    tax_entity: str | None = None
    effective_date: str | None = None
    state: str | None = None
    lobs: str | None = None
    enroll_providers: bool | None = None
    group_providers: list[str] | None = None
    primary_practice_location: str | None = None
    other_practice_locations: list[str] | None = None
    notes: str | None = None
    request_type: str | None = None


class ProviderEnrollmentRequestCreate(BaseModel):
    """Payload for creating a provider enrollment request.

    The spec marks ``tax_entity``, ``state``, ``health_plan``, ``lobs``, ``provider``,
    ``primary_practice_location`` and ``request_type`` as required; they remain optional here
    for backward compatibility.

    Note:
        ``practice_location`` and ``effective_date`` are not part of the documented spec and are
        kept only for backward compatibility; prefer ``primary_practice_location``.
    """

    provider: str | None = None
    health_plan: str | None = None
    practice_location: str | None = None
    tax_entity: str | None = None
    effective_date: str | None = None
    state: str | None = None
    lobs: str | None = None
    primary_practice_location: str | None = None
    other_practice_locations: list[str] | None = None
    notes: str | None = None
    request_type: str | None = None


class ExistingProviderEnrollmentCreate(BaseModel):
    """Payload for adding an existing provider enrollment.

    The spec additionally marks ``client`` as required; it remains optional here for backward
    compatibility. ``lobs`` and ``effective_date`` were loosened to optional to match the
    documented spec (which accepts a comma-separated string for ``lobs``).
    """

    provider: str
    tax_entity: str
    state: str
    health_plan: str
    lobs: list[str] | str | None = None
    other_practice_locations: list[str] | None = None
    primary_practice_location: str
    par_status: str
    new_health_plan_id: str | None = None
    effective_date: str | None = None
    no_re_validation_date: bool | None = None
    re_validation_date: str | None = None
    no_proof_of_enrollment: bool | None = None
    proof_of_enrollments: str | None = None
    notes: str | None = None
    id: str | None = None
    no_health_plan_id: bool | None = None
    welcome_letters: list[Any] | str | None = None
    contract_files: list[Any] | str | None = None
    fee_structures: list[Any] | str | None = None
    client: str | None = None


class ExistingProviderEnrollment(BaseModel):
    """Response returned when an existing provider enrollment is created.

    All fields are optional — the spec marks nothing required on the 201
    response, and SDK response models stay permissive by convention.
    """

    id: str | None = None
    provider: str | None = None
    tax_entity: str | None = None
    state: str | None = None
    health_plan: str | None = None
    lobs: list[str] | str | None = None
    other_practice_locations: list[str] | None = None
    primary_practice_location: str | None = None
    par_status: str | None = None
    new_health_plan_id: str | None = None
    effective_date: str | None = None
    no_re_validation_date: bool | None = None
    re_validation_date: str | None = None
    no_proof_of_enrollment: bool | None = None
    proof_of_enrollments: str | None = None
    notes: str | None = None
    no_health_plan_id: bool | None = None
    welcome_letters: list[Any] | str | None = None
    contract_files: list[Any] | str | None = None
    fee_structures: list[Any] | str | None = None
    client: str | None = None


class ExistingGroupEnrollmentCreate(BaseModel):
    """Payload for adding an existing group enrollment."""

    tax_entity: str
    state: str
    health_plan: str
    primary_practice_location: str
    par_status: str
    client: str
    other_practice_locations: list[str] | None = None
    no_health_plan_id: bool | None = None
    new_health_plan_id: str | None = None
    effective_date: str | None = None
    no_re_validation_date: bool | None = None
    re_validation_date: str | None = None
    no_proof_of_enrollment: bool | None = None
    proof_of_enrollments: str | None = None
    lobs: str | None = None
    notes: str | None = None
    welcome_letters: str | None = None
    contract_files: str | None = None
    fee_structures: str | None = None


class ExistingGroupEnrollment(BaseModel):
    """Response returned when an existing group enrollment is created.

    All fields are optional — the spec marks nothing required on the 201
    response, and SDK response models stay permissive by convention.
    """

    id: str | None = None
    tax_entity: str | None = None
    state: str | None = None
    health_plan: str | None = None
    primary_practice_location: str | None = None
    par_status: str | None = None
    client: str | None = None
    other_practice_locations: list[str] | None = None
    no_health_plan_id: bool | None = None
    new_health_plan_id: str | None = None
    effective_date: str | None = None
    no_re_validation_date: bool | None = None
    re_validation_date: str | None = None
    no_proof_of_enrollment: bool | None = None
    proof_of_enrollments: str | None = None
    lobs: str | None = None
    notes: str | None = None
    welcome_letters: str | None = None
    contract_files: str | None = None
    fee_structures: str | None = None


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


class GroupProviderRef(BaseModel):
    """Provider reference embedded in an enrollment request detail."""

    id: str | None = None
    full_name: str | None = None


class EnrollmentRequestDetail(BaseModel):
    """Full detail of a payer enrollment request."""

    id: str | None = None
    request_id: str | None = None
    enrollment_type: str | None = None
    status: str | None = None
    created_at: datetime | None = None
    health_plan_name: str | None = None
    health_plan_id: str | None = None
    followup_oa_completed_at: datetime | None = None
    created_by: str | None = None
    status_reason: str | None = None
    tax_entity_name: str | None = None
    client_name: str | None = None
    last_submission_oa: str | None = None
    last_followup_oa: str | None = None
    submission_oa_submitted_at: datetime | None = None
    primary_practice_location_name: str | None = None
    submission_oa_name: str | None = None
    followup_oa_name: str | None = None
    submission_oa: str | None = None
    followup_oa: str | None = None
    state: str | None = None
    submission_type: str | None = None
    other_practice_location_names: list[str] | None = None
    notes: str | None = None
    created_by_name: str | None = None
    retrigger_attempts: int | None = None
    request_type: str | None = None
    provider: str | None = None
    provider_name: str | None = None
    group_providers: list[GroupProviderRef] | None = None
    client: str | None = None
    oa_actions_available: dict[str, Any] | None = None
    ongoing_tasks: bool | None = None
    caqh_audit_status: str | None = None
    caqh_audit_id: str | None = None
    billing_enabled: bool | None = None
    current_contracting_sub_status: str | None = None


class EnrollmentRequestStatusUpdate(BaseModel):
    """Payload for updating an enrollment request status (e.g. cancelling it).

    Note:
        ``note`` is mandatory when ``status_reason`` is ``"OTHER"``.
    """

    status: str | None = None
    status_reason: str | None = None
    note: str | None = None


class EnrollmentTimelineEntry(BaseModel):
    """A single enrollment request timeline entry."""

    id: str | None = None
    enrollment_request: str | None = None
    change_type: str | None = None
    status: str | None = None
    updated_by: str | None = None
    created_at: datetime | None = None
    assignee: str | None = None
    updated_by_full_name: str | None = None
    assignee_full_name: str | None = None
    note: str | None = None
    change_description: str | None = None
    client: str | None = None
    status_reason: str | None = None
    submission_application_id: str | None = None
    followup_date: str | None = None
    retrigger_reference: str | None = None
    semi_automatic_enrollment_request_reference: str | None = None
    full_automatic_enrollment_request_reference: str | None = None
    retrigger_reference_details: dict[str, Any] | None = None
    followup_mode: str | None = None
    context: str | None = None
    followup_phone: str | None = None
    followup_email: str | None = None
    proof_of_documents: list[str] | None = None
    welcome_letters: list[str] | None = None
    contract_files: list[str] | None = None
    fee_structures: list[str] | None = None
    contracting_status: str | None = None
    contracting_old_status: str | None = None
    contracting_status_files: str | None = None
    on_hold_next_action_date: str | None = None


class EnrollmentTimelineParams(BaseModel):
    """Query parameters for the enrollment request timeline list.

    ``change_type`` accepts: ASSIGNEE_CHANGE, CONTRACTING_STATUS_CHANGE,
    ENROLLMENT_APPLICATION_FORM_FAILURE, FOLLOWUP_EMAIL, NEW_FOLLOWUP, PROCESSING_ERROR,
    RETRIGGER, STATUS_CHANGE.
    """

    assignee: str | None = None
    change_type: str | None = None
    created_at: str | None = None
    enrollment_request: str | None = None
    limit: int | None = None
    offset: int | None = None
    search: str | None = None
    status: str | None = None
    updated_by: str | None = None


class SelectableOaUser(BaseModel):
    """An Operations Analyst user selectable for enrollment request reassignment."""

    id: str | None = None
    oa_full_name: str | None = None


class BulkOaAssignment(BaseModel):
    """Payload for bulk OA assignment to payer enrollment requests.

    ``request_phase`` items accept ``SUBMISSION_PHASE`` (targets ``submission_oa``) and
    ``FOLLOWUP_PHASE`` (targets ``followup_oa``). Requests can be targeted explicitly via
    ``enrollment_request_ids`` and/or filtered by ``health_plan_ids`` and ``states``.
    """

    oas_to_assign: list[str]
    request_phase: list[str]
    enrollment_request_ids: list[str] | None = None
    health_plan_ids: list[str] | None = None
    states: list[str] | None = None


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
