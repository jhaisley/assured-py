# Provider Profile

Several endpoints in this module are now officially documented in the platform
OpenAPI spec (personal info, employment v1, encrypted SSN, provider documents).
Recent additions and changes:

- `list_documents()` / `list_documents_all()` / `list_documents_df()` — list provider documents (`GET /api/v1/users/provider-documents/`, new in the spec).
- `get_ssn()` — retrieve the encrypted SSN record (JWT Bearer auth; the returned `ssn` is ciphertext).
- `update_ssn()` — still applies AES-256-CTR encryption keyed from the session JWT; the spec documents the endpoint but not the encryption requirement.
- `update_personal_info()` — still fetch-merge-patches the full payload; response-only fields are now stripped before PATCH.
- Create models gained new spec fields: `document` on education, licenses, DEA, CDS, Medicaid, Medicare, and professional training; `is_available` (DEA); `license_unlimited` (CDS); `maintenance_of_certification` (certifications); `training_type` / `speciality` and related address fields (professional training); `file_checksum`, `uploaded_date`, `expiration_date`, `state` (provider documents).
- Large spec enums (degree, speciality, certifying board, document type, state, license type) are intentionally kept as plain strings.

## Resource

::: assured.resources.provider_profile.ProviderProfileResource

## Models

::: assured.models.provider_profile.ProviderPersonalInfo

::: assured.models.provider_profile.ProviderPersonalInfoUpdate

::: assured.models.provider_profile.Certification

::: assured.models.provider_profile.CertificationCreate

::: assured.models.provider_profile.License

::: assured.models.provider_profile.LicenseCreate

::: assured.models.provider_profile.DEARecord

::: assured.models.provider_profile.DEARecordCreate

::: assured.models.provider_profile.CDSRecord

::: assured.models.provider_profile.CDSRecordCreate

::: assured.models.provider_profile.MedicaidRecord

::: assured.models.provider_profile.MedicaidRecordCreate

::: assured.models.provider_profile.MedicareRecord

::: assured.models.provider_profile.MedicareRecordCreate

::: assured.models.provider_profile.Employment

::: assured.models.provider_profile.EmploymentCreate

::: assured.models.provider_profile.GapHistory

::: assured.models.provider_profile.GapHistoryCreate

::: assured.models.provider_profile.Education

::: assured.models.provider_profile.EducationCreate

::: assured.models.provider_profile.ProfessionalTraining

::: assured.models.provider_profile.ProfessionalTrainingCreate

::: assured.models.provider_profile.ProfessionalLiabilityInsurance

::: assured.models.provider_profile.ProfessionalLiabilityInsuranceCreate

::: assured.models.provider_profile.ProviderDocument

::: assured.models.provider_profile.ProviderDocumentCreate
