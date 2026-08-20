"""Provider profile models (certifications, licenses, IDs, education, etc.)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

# ---- Personal Info ----


class ProviderPersonalInfo(BaseModel):
    """Provider personal information (GET response).

    Documented at ``GET /api/v1/users/provider-personal-info/{id}/``
    (previously undocumented). The ``id`` path parameter is the *provider
    profile* ID, not the provider account ID.

    Notes:
        ``gender`` is a 7-value enum; ``hair_color`` / ``eye_color`` are 9-value
        enums; ``management_type`` is one of ``PROVIDER_MANAGED`` /
        ``ADMIN_MANAGED``. All are kept as plain strings for permissiveness.
    """

    id: str | None = None
    full_name: str | None = None
    nucc_grouping: str | None = None
    nucc_taxonomy_code: str | None = None
    nucc_classification: str | None = None
    specialization: str | None = None
    provider_type: str | None = None
    provider_role: str | None = None
    practice_setting: str | None = None
    primary_practice_state: str | None = None
    languages: list[str] | None = None
    additional_practice_states: list[str] | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    suffix: str | None = None
    home_street_address_1: str | None = None
    home_street_address_2: str | None = None
    home_city: str | None = None
    home_state: str | None = None
    home_zip_code: str | None = None
    home_country: str | None = None
    primary_email_address: str | None = None
    public_email: str | None = None
    personal_email: str | None = None
    business_email: str | None = None
    other_email: str | None = None
    other_emails: list[Any] | None = None
    other_names: list[Any] | None = None
    primary_phone: str | None = None
    individual_npi: str | None = None
    caqh_id: str | None = None
    last_caqh_attestation_date: date | None = None
    ssn: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    us_citizen: bool | None = None
    birth_country: str | None = None
    birth_state: str | None = None
    birth_city: str | None = None
    race: str | None = None
    county: str | None = None
    height_inches: int | None = None
    weight_in_lbs: int | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    supervising_or_collaborative_physician_name: str | None = None
    physician_individual_npi: str | None = None
    home_phone_number: str | None = None
    fax_number: str | None = None
    correspondence_address_same_as_residence: bool | None = None
    correspondence_street_address_1: str | None = None
    correspondence_street_address_2: str | None = None
    correspondence_city: str | None = None
    correspondence_state: str | None = None
    correspondence_country: str | None = None
    correspondence_postal_code: str | None = None
    upin: str | None = None
    visa_number: str | None = None
    visa_status: str | None = None
    citizenship_country: str | None = None
    eligible_to_work_in_us: bool | None = None
    served_military: bool | None = None
    active_or_reserve_duty: bool | None = None
    date_of_service_start: date | None = None
    date_of_service_end: date | None = None
    last_location_of_service: str | None = None
    branch_of_service: str | None = None
    is_ecfmg: bool | None = None
    ecfmg_number: str | None = None
    ecfmg_issue_date: date | None = None
    personal_completion_info: dict[str, Any] | None = None
    credentialing_readiness_info: dict[str, Any] | None = None
    management_type: str | None = None
    updated_at: datetime | None = None


class ProviderPersonalInfoUpdate(BaseModel):
    """Payload for ``PATCH /api/v1/users/provider-personal-info/{id}/`` (now documented).

    All fields optional — only set what you want to change; the SDK's
    fetch-merge-patch helper (``update_personal_info``) fills in the rest,
    because production requires the complete payload on every PATCH.

    Notes:
        ``ssn`` is not part of the documented PATCH schema — production
        SSN updates go through ``update_ssn()`` (encrypted endpoint). The
        field is retained here for backward compatibility only.
    """

    full_name: str | None = None
    nucc_grouping: str | None = None
    nucc_taxonomy_code: str | None = None
    nucc_classification: str | None = None
    specialization: str | None = None
    provider_type: str | None = None
    provider_role: str | None = None
    practice_setting: str | None = None
    primary_practice_state: str | None = None
    languages: list[str] | None = None
    additional_practice_states: list[str] | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    suffix: str | None = None
    home_street_address_1: str | None = None
    home_street_address_2: str | None = None
    home_city: str | None = None
    home_state: str | None = None
    home_zip_code: str | None = None
    home_country: str | None = None
    primary_email_address: str | None = None
    public_email: str | None = None
    personal_email: str | None = None
    business_email: str | None = None
    other_email: str | None = None
    primary_phone: str | None = None
    individual_npi: str | None = None
    caqh_id: str | None = None
    ssn: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    us_citizen: bool | None = None
    birth_country: str | None = None
    birth_state: str | None = None
    birth_city: str | None = None
    race: str | None = None
    county: str | None = None
    height_inches: int | None = None
    weight_in_lbs: int | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    supervising_or_collaborative_physician_name: str | None = None
    physician_individual_npi: str | None = None
    home_phone_number: str | None = None
    fax_number: str | None = None
    correspondence_address_same_as_residence: bool | None = None
    correspondence_street_address_1: str | None = None
    correspondence_street_address_2: str | None = None
    correspondence_city: str | None = None
    correspondence_state: str | None = None
    correspondence_country: str | None = None
    correspondence_postal_code: str | None = None
    upin: str | None = None
    visa_number: str | None = None
    visa_status: str | None = None
    citizenship_country: str | None = None
    eligible_to_work_in_us: bool | None = None
    served_military: bool | None = None
    active_or_reserve_duty: bool | None = None
    date_of_service_start: date | None = None
    date_of_service_end: date | None = None
    last_location_of_service: str | None = None
    branch_of_service: str | None = None
    is_ecfmg: bool | None = None
    ecfmg_number: str | None = None
    ecfmg_issue_date: date | None = None
    credentialing_readiness_info: dict[str, Any] | None = None


# ---- Certifications ----


class Certification(BaseModel):
    """Provider board certification record."""

    id: str | None = None
    speciality: str | None = None
    certifying_board_name: str | None = None
    number: str | None = None
    initial_date: date | None = None
    expiration_date: date | None = None
    speciality_level: str | None = None
    document: str | None = None
    provider: str | None = None
    recertification_date: date | None = None
    is_board_certified: bool | None = None
    not_board_certified_reason: str | None = None
    maintenance_of_certification: bool | None = None
    list_in_hmo_directory: bool | None = None
    list_in_ppo_directory: bool | None = None
    list_in_pos_directory: bool | None = None
    other_practice_interest_or_focus: str | None = None
    board_exam_date: date | None = None


class CertificationCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-certifications/``.

    Notes:
        ``speciality`` (696 values) and ``certifying_board_name`` (116 values)
        are large spec enums kept as plain strings. ``speciality_level`` is one
        of ``PRIMARY`` / ``SECONDARY`` / ``ADDITIONAL``.
        ``not_board_certified_reason`` is one of ``TAKEN_EXAM_RESULT_PENDING``,
        ``TAKEN_PART_I_ELIGIBLE_FOR_PART_II``, ``INTENDING_TO_SIT_IN_BOARDS``,
        ``NOT_PLANNING_BOARDS``.
    """

    provider: str
    speciality: str | None = None
    certifying_board_name: str | None = None
    number: str | None = None
    initial_date: date | None = None
    expiration_date: date | None = None
    speciality_level: str | None = None
    document: str | None = None
    recertification_date: date | None = None
    is_board_certified: bool | None = None
    not_board_certified_reason: str | None = None
    maintenance_of_certification: bool | None = None
    list_in_hmo_directory: bool | None = None
    list_in_ppo_directory: bool | None = None
    list_in_pos_directory: bool | None = None
    other_practice_interest_or_focus: str | None = None
    board_exam_date: date | None = None


# ---- License ----


class License(BaseModel):
    """Provider professional license record."""

    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_type: str | None = None
    provider: str | None = None
    override_licenses_status: str | None = None
    is_currently_practicing_in_state: bool | None = None
    document: str | None = None


class LicenseCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-ids-license/``.

    Notes:
        ``state`` (56 values) and ``license_type`` (87 values) are spec enums
        kept as plain strings.
    """

    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_type: str | None = None
    override_licenses_status: str | None = None
    is_currently_practicing_in_state: bool | None = None
    document: str | None = None


# ---- DEA ----


class DEARecord(BaseModel):
    """Provider DEA registration record."""

    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_unlimited: bool | None = None
    provider: str | None = None
    document: str | None = None
    is_available: bool | None = None


class DEARecordCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-ids-dea/``.

    Notes:
        ``state`` is a 56-value spec enum kept as a plain string.
    """

    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_unlimited: bool | None = None
    document: str | None = None
    is_available: bool | None = None


# ---- CDS ----


class CDSRecord(BaseModel):
    """Provider CDS registration record."""

    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    provider: str | None = None
    is_currently_practicing_in_state: bool | None = None
    license_unlimited: bool | None = None
    document: str | None = None


class CDSRecordCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-ids-cds/``.

    Notes:
        ``state`` is a 56-value spec enum kept as a plain string.
    """

    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    is_currently_practicing_in_state: bool | None = None
    license_unlimited: bool | None = None
    document: str | None = None


# ---- Medicaid ----


class MedicaidRecord(BaseModel):
    """Provider Medicaid ID record."""

    id: str | None = None
    state: str | None = None
    number: str | None = None
    provider: str | None = None
    document: str | None = None


class MedicaidRecordCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-ids-medicaid/``."""

    provider: str
    state: str | None = None
    number: str | None = None
    document: str | None = None


# ---- Medicare ----


class MedicareRecord(BaseModel):
    """Provider Medicare ID record."""

    id: str | None = None
    state: str | None = None
    number: str | None = None
    provider: str | None = None
    document: str | None = None


class MedicareRecordCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-ids-medicare/``."""

    provider: str
    state: str | None = None
    number: str | None = None
    document: str | None = None


# ---- Employment ----


class Employment(BaseModel):
    """Provider employment record.

    Backed by ``/api/v1/users/provider-employment-v1/`` (now officially
    documented; the legacy ``/provider-employments/`` endpoint was removed
    from the spec).

    Notes:
        ``position``, ``type``, ``is_current`` and ``reason_for_leaving`` are
        legacy fields retained for backward compatibility; they are not part
        of the official v1 schema (``currently_employed`` and
        ``reason_for_discontinuance`` are the documented equivalents).
    """

    id: str | None = None
    employer_name: str | None = None
    position: str | None = None
    type: str | None = None
    currently_employed: bool | None = None
    is_current: bool | None = None  # Legacy; superseded by currently_employed
    start_date: date | None = None
    end_date: date | None = None
    gap_explanation: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zip_code: str | None = None
    phone_number: str | None = None
    email_address: str | None = None
    contact_information: str | None = None
    provider: str | None = None
    reason_for_discontinuance: str | None = None
    reason_for_leaving: str | None = None  # Legacy; superseded by reason_for_discontinuance
    document: str | None = None


class EmploymentCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-employment-v1/`` (now documented).

    Notes:
        ``position``, ``type``, ``is_current`` and ``reason_for_leaving`` are
        legacy fields not present in the official v1 request schema; prefer
        ``currently_employed`` and ``reason_for_discontinuance``.
        ``gap_explanation`` appears only in the documented response schema,
        not the request schema, but production has historically required it
        on create (see API_Divergence.md), so it is kept on the payload.
    """

    provider: str
    employer_name: str | None = None
    position: str | None = None
    type: str | None = None
    currently_employed: bool | None = None
    is_current: bool | None = None
    start_date: date | None = None
    end_date: date | None = None
    gap_explanation: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zip_code: str | None = None
    phone_number: str | None = None
    email_address: str | None = None
    contact_information: str | None = None
    reason_for_discontinuance: str | None = None
    reason_for_leaving: str | None = None
    document: str | None = None


# ---- Gap History ----


class GapHistory(BaseModel):
    """Provider gap history record.

    Notes:
        The official spec calls the explanation field ``gap_explanation``;
        ``reason`` is retained for backward compatibility.
    """

    id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None  # Legacy; spec field is gap_explanation
    gap_explanation: str | None = None
    provider: str | None = None


class GapHistoryCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-gap-history/``."""

    provider: str
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None  # Legacy; spec field is gap_explanation
    gap_explanation: str | None = None


# ---- Education ----


class Education(BaseModel):
    """Provider education record."""

    id: str | None = None
    name: str | None = None
    institution_name: str | None = None  # Legacy; spec field is name
    degree: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    is_primary: bool | None = None
    address_street_1: str | None = None
    address_street_2: str | None = None
    postal_code: str | None = None
    document: str | None = None
    provider: str | None = None


class EducationCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-education/``.

    Notes:
        ``degree`` is an 86-value spec enum kept as a plain string.
        ``institution_name`` is a legacy alias retained for backward
        compatibility; the official schema uses ``name``.
    """

    provider: str
    name: str | None = None
    institution_name: str | None = None
    degree: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    is_primary: bool | None = None
    address_street_1: str | None = None
    address_street_2: str | None = None
    postal_code: str | None = None
    document: str | None = None


# ---- Professional Training ----


class ProfessionalTraining(BaseModel):
    """Provider professional training record.

    Notes:
        ``program_type`` and ``specialty`` are legacy fields retained for
        backward compatibility; the official schema uses ``training_type``
        and ``speciality``.
    """

    id: str | None = None
    institution_name: str | None = None
    program_type: str | None = None  # Legacy; spec field is training_type
    specialty: str | None = None  # Legacy; spec field is speciality
    training_type: str | None = None
    speciality: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    street_1: str | None = None
    street_2: str | None = None
    postal_code: str | None = None
    country: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_program_successfully_completed: bool | None = None
    program_director: str | None = None
    current_program_director: str | None = None
    document: str | None = None
    provider: str | None = None


class ProfessionalTrainingCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-professional-training/``.

    Notes:
        ``training_type`` is one of ``Internship``, ``Residency``,
        ``Fellowship``, ``Other Training``, ``Continuing Medical Education``,
        ``Faculty Positions / Academic Appointments``.
        ``program_type`` and ``specialty`` are legacy aliases retained for
        backward compatibility (spec uses ``training_type`` / ``speciality``).
    """

    provider: str
    institution_name: str | None = None
    program_type: str | None = None  # Legacy; spec field is training_type
    specialty: str | None = None  # Legacy; spec field is speciality
    training_type: str | None = None
    speciality: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    street_1: str | None = None
    street_2: str | None = None
    postal_code: str | None = None
    country: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_program_successfully_completed: bool | None = None
    program_director: str | None = None
    current_program_director: str | None = None
    document: str | None = None


# ---- Documents ----


class ProviderDocument(BaseModel):
    """Provider document association record."""

    id: str | None = None
    provider: str | None = None
    document_name: str | None = None
    document_type: str | None = None
    document_url: str | None = None
    document_file: str | None = None
    file_checksum: str | None = None
    uploaded_date: str | None = None
    expiration_date: str | None = None
    state: str | None = None
    presigned_document_url: str | None = None


class ProviderDocumentCreate(BaseModel):
    """Payload for ``POST /api/v1/users/provider-documents/`` (now documented).

    Notes:
        ``document_type`` is a 92-value spec enum kept as a plain string.
        Production still requires JWT Bearer auth on this endpoint (see
        ``API_Divergence.md`` section 8).
    """

    provider: str
    document_name: str | None = None
    document_type: str | None = None
    document_url: str | None = None
    document_file: str | None = None
    file_checksum: str | None = None
    uploaded_date: str | None = None
    expiration_date: str | None = None
    state: str | None = None


# ---- Professional Liability Insurance ----


class ProfessionalLiabilityInsurance(BaseModel):
    """A professional liability insurance policy.

    Field names follow the documented schema for
    ``/api/v1/users/provider-professional-liability-insurances/``. The
    ``carrier_name`` / ``coverage_amount_*`` / ``effective_date`` /
    ``expiration_date`` fields are legacy SDK aliases kept for backward
    compatibility and are not part of the documented schema.
    """

    id: str | None = None
    policy_number: str | None = None
    name: str | None = None
    current_effective_date: date | None = None
    current_expiration_date: date | None = None
    per_occurence_limit: float | None = None
    aggregate_limit: float | None = None
    document: str | None = None
    provider: str | None = None
    is_self_insured: bool | None = None
    address_street_1: str | None = None
    address_street_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    phone_number: str | None = None
    coverage_type: str | None = None
    length_of_time_with_carrier: str | None = None
    # Legacy SDK fields (pre-spec-update), not in the documented schema.
    carrier_name: str | None = None
    coverage_amount_per_occurrence: str | None = None
    coverage_amount_aggregate: str | None = None
    effective_date: date | None = None
    expiration_date: date | None = None


class ProfessionalLiabilityInsuranceCreate(BaseModel):
    """Payload for creating a professional liability insurance policy.

    Uses the documented schema field names (``name``,
    ``current_effective_date``, ``per_occurence_limit``, …). Legacy SDK
    field names are retained for backward compatibility but are ignored by
    the documented endpoint.
    """

    provider: str
    policy_number: str | None = None
    name: str | None = None
    current_effective_date: date | None = None
    current_expiration_date: date | None = None
    per_occurence_limit: float | None = None
    aggregate_limit: float | None = None
    document: str | None = None
    is_self_insured: bool | None = None
    address_street_1: str | None = None
    address_street_2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    phone_number: str | None = None
    coverage_type: str | None = None
    length_of_time_with_carrier: str | None = None
    # Legacy SDK fields (pre-spec-update), not in the documented schema.
    carrier_name: str | None = None
    coverage_amount_per_occurrence: str | None = None
    coverage_amount_aggregate: str | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
