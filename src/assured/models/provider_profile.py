"""Provider profile models (certifications, licenses, IDs, education, etc.)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

# ---- Personal Info ----


class ProviderPersonalInfo(BaseModel):
    """Provider personal information (GET response)."""

    nucc_grouping: str | None = None
    provider_type: str | None = None
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
    primary_email_address: str | None = None
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
    citizenship_country: str | None = None
    eligible_to_work_in_us: bool | None = None
    served_military: bool | None = None
    date_of_service_start: date | None = None
    date_of_service_end: date | None = None
    last_location_of_service: str | None = None
    branch_of_service: str | None = None
    is_ecfmg: bool | None = None
    ecfmg_number: str | None = None
    ecfmg_issue_date: date | None = None


class ProviderPersonalInfoUpdate(BaseModel):
    """Payload for PATCH /provider-personal-info/{id}/.

    All fields optional — only send what you want to change.
    """

    nucc_grouping: str | None = None
    provider_type: str | None = None
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
    primary_email_address: str | None = None
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
    citizenship_country: str | None = None
    eligible_to_work_in_us: bool | None = None
    served_military: bool | None = None
    date_of_service_start: date | None = None
    date_of_service_end: date | None = None
    last_location_of_service: str | None = None
    branch_of_service: str | None = None
    is_ecfmg: bool | None = None
    ecfmg_number: str | None = None
    ecfmg_issue_date: date | None = None


# ---- Certifications ----


class Certification(BaseModel):
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
    list_in_hmo_directory: bool | None = None
    list_in_ppo_directory: bool | None = None
    list_in_pos_directory: bool | None = None
    other_practice_interest_or_focus: str | None = None
    board_exam_date: date | None = None


# ---- License ----


class License(BaseModel):
    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_type: str | None = None
    provider: str | None = None
    override_licenses_status: str | None = None
    is_currently_practicing_in_state: bool | None = None


class LicenseCreate(BaseModel):
    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_type: str | None = None
    override_licenses_status: str | None = None
    is_currently_practicing_in_state: bool | None = None


# ---- DEA ----


class DEARecord(BaseModel):
    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_unlimited: bool | None = None
    provider: str | None = None


class DEARecordCreate(BaseModel):
    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    license_unlimited: bool | None = None


# ---- CDS ----


class CDSRecord(BaseModel):
    id: str | None = None
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    provider: str | None = None
    is_currently_practicing_in_state: bool | None = None


class CDSRecordCreate(BaseModel):
    provider: str
    state: str | None = None
    number: str | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    is_currently_practicing_in_state: bool | None = None


# ---- Medicaid ----


class MedicaidRecord(BaseModel):
    id: str | None = None
    state: str | None = None
    number: str | None = None
    provider: str | None = None


class MedicaidRecordCreate(BaseModel):
    provider: str
    state: str | None = None
    number: str | None = None


# ---- Medicare ----


class MedicareRecord(BaseModel):
    id: str | None = None
    state: str | None = None
    number: str | None = None
    provider: str | None = None


class MedicareRecordCreate(BaseModel):
    provider: str
    state: str | None = None
    number: str | None = None


# ---- Employment ----


class Employment(BaseModel):
    id: str | None = None
    employer_name: str | None = None
    position: str | None = None
    type: str | None = None
    currently_employed: bool | None = None
    is_current: bool | None = None  # Keeping for backwards compatibility if needed
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
    reason_for_leaving: str | None = None  # Keeping for backward compatibility
    document: str | None = None


class EmploymentCreate(BaseModel):
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
    id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None
    provider: str | None = None


class GapHistoryCreate(BaseModel):
    provider: str
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = None


# ---- Education ----


class Education(BaseModel):
    id: str | None = None
    name: str | None = None
    institution_name: str | None = None  # Keeping for backward compatibility
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
    provider: str | None = None


class EducationCreate(BaseModel):
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


# ---- Professional Training ----


class ProfessionalTraining(BaseModel):
    id: str | None = None
    institution_name: str | None = None
    program_type: str | None = None
    specialty: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    provider: str | None = None


class ProfessionalTrainingCreate(BaseModel):
    provider: str
    institution_name: str | None = None
    program_type: str | None = None
    specialty: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# ---- Documents ----


class ProviderDocument(BaseModel):
    id: str | None = None
    provider: str | None = None
    document_name: str | None = None
    document_type: str | None = None
    document_url: str | None = None
    document_file: str | None = None
    uploaded_date: str | None = None
    expiration_date: str | None = None
    state: str | None = None
    presigned_document_url: str | None = None


class ProviderDocumentCreate(BaseModel):
    provider: str
    document_name: str | None = None
    document_type: str | None = None
    document_url: str | None = None


# ---- Professional Liability Insurance ----


class ProfessionalLiabilityInsurance(BaseModel):
    id: str | None = None
    carrier_name: str | None = None
    policy_number: str | None = None
    coverage_amount_per_occurrence: str | None = None
    coverage_amount_aggregate: str | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    provider: str | None = None


class ProfessionalLiabilityInsuranceCreate(BaseModel):
    provider: str
    carrier_name: str | None = None
    policy_number: str | None = None
    coverage_amount_per_occurrence: str | None = None
    coverage_amount_aggregate: str | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
