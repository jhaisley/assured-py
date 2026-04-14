# Assured Platform API — Spec vs Reality

This document outlines the known discrepancies between the official OpenAPI specification (`Assured Platform API.json`) and the actual operational behavior of the production Assured Platform API as implemented in the `assured` SDK.

---

> [!WARNING]
> These endpoints and payloads deviate from the documented spec. The `assured` SDK has been built to support **actual** production behavior, superseding the official OpenAPI schema in these cases.

## 1. Provider Personal Info (`provider-personal-info`)

**Spec:** Undocumented entirely in the OpenAPI spec.
**Reality:** The API exposes comprehensive GET and PATCH endpoints used to manage a provider's primary demographic, descriptive, and background context forms.

- **Methods:** `GET /api/v1/users/provider-personal-info/{profile_id}/` and `PATCH`.
- **Payload/Model:** Contains 55 fields encompassing demographics (name, DOB, SSN, NPI, CAQH ID), residency addresses, correspondence addresses, practice settings, languages, ECFMG status, visa/citizenship details, and military service records. 
- **Quirk:** The API requires the *complete* model payload when making `PATCH` requests; omitting unmodified existing fields will trigger `HTTP 400 Validation Error`. Furthermore, `null` must be used strictly for nullable fields rather than omitting the key. The SDK's `update_personal_info` handles this automatically via fetch-merge-patch.

## 2. Provider Employment Endpoints

**Spec:** Documented as `GET / POST / PATCH / DELETE` on `/api/v1/users/provider-employments/`.
**Reality:** The platform has silently migrated to a `v1` endpoint for provider employments that carries a drastically different schema.

- **Endpoint:** Instead of `/api/v1/users/provider-employments/`, the API expects `/api/v1/users/provider-employment-v1/`.
- **Schema Differences:** The new endpoint requires/returns many additional and renamed fields.
  - *Deprecated/Replaced Fields:* `is_current` (now `currently_employed`), `reason_for_leaving` (now `reason_for_discontinuance`).
  - *New Fields explicitly required:* `type`, `gap_explanation`, `address`, `city`, `state`, `country`, `zip_code`, `phone_number`, `email_address`, `contact_information`, `document`.
- **Compatibility:** The SDK models (`Employment` and `EmploymentCreate`) include both the new specific `v1` fields and the older schema fields to ensure backward compatibility.

## 3. Provider Education Endpoints

**Spec:** The schema defines a simple model containing `institution_name`, `degree`, `start_date`, and `end_date`.
**Reality:** The actual endpoint requires a much richer location-oriented schema to track the exact identity and place of education.

- **Schema Differences:**
  - *Deprecated/Replaced Fields:* `institution_name` generally superseded by `name`.
  - *New Fields added:* `city`, `state`, `country`, `is_primary`, `address_street_1`, `address_street_2`, `postal_code`.
- **Compatibility:** Like employment, the SDK integrates these richer properties onto the SDK `Education` models while preserving `institution_name` for legacy use.

## 4. Provider Account vs Provider Profile IDs

**Spec:** Often implies a generic "Provider ID" is passed across routes.
**Reality:** The API is highly sensitive to the distinction between a Provider Account and a Provider Profile.

- **Provider Account ID:** The core identity record (UUID), passed to the list and invite endpoints.
- **Provider Profile ID:** A separate UUID 1:1 linked to the account, which must be used for nearly all `provider_profile` domains (Personal Info, Certifications, Licenses, Insurance, etc.). Mixing them up causes the API to fail with `404` or `422`.
- **SDK Solution:** Built a dedicated resolution helper via `client.providers.get_profile_id(account_id)` to gracefully bridge this gap automatically.

## 5. Encrypted SSN Endpoint

**Spec:** Not documented in the API behavior.
**Reality:** The platform requires SSNs to be submitted as a symmetrically encrypted token rather than plaintext.

- **Endpoint:** `PATCH /api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{provider_profile_id}/`
- **Authentication:** Ironically, this specific profile endpoint rejects standard API Keys and strictly requires standard `Authorization: Bearer {jwt}` headers using a valid session JWT token.
- **Payload & Encryption:** 
  - Expects `{"ssn": "<Base64 Encoded Ciphertext>"}`
  - The ciphertext must be encoded using an `AES-256-CTR` standard.
  - The symmetric key is dynamically generated via a `SHA256` hash of the provided JWT token.
  - A random 16-byte `IV` is prefixed against the ciphertext before Base64 encoding.

## 6. JWT Generation (Login)

**Spec:** No programmatic configuration or endpoint for acquiring Session JWTs.
**Reality:** The frontend relies on an undocumented login endpoint to generate the required JWTs.

- **Endpoint:** `POST /api/v1/users/login/`
- **Payload:** `{"email": "...", "password": "...", "remember": true}`
- **SDK Solution:** Exposed `await client.users.login(email, password)` and integrated a lazy caching mechanism securely into the `AssuredClient`. The client pulls credentials via `pydantic-settings` (`ASSURED_USER` and `ASSURED_PASS`) from the environment, automating JWT injection when standard API Key authentication isn't enough.

## 7. File Uploads and Presigned URLs

**Spec:** The OpenAPI spec expects generic REST models.
**Reality:** The entire document handling subsystem is built on heavily customized AWS storage APIs driven through the Assured Django interface.

- **Storage Extraction:** Files must be uploaded to `/api/v1/files/handle/` using a raw `multipart/form-data` payload containing a UUID `name` key, and the binary data under `file`. This endpoint specifically enforces JWT Bearer authentication. It returns an `s3://` object reference (`file_url`).
- **Temporary Access:** Due to S3 protections, URLs cannot be exposed safely. The SDK invokes `/api/v1/files/presign-s3-url/presign_s3_url/` feeding it back the `s3://` path which brokers a limited-time publicly accessible URL.

## 8. Provider Document Associations

**Spec:** Documents are typically grouped loosely without strict multi-stage processes explicitly outlined.
**Reality:** Linking an actual file binary to a Provider Profile is a two-step process.

- **Process:** 
  1. The user must first process the raw file via the JWT-restricted route `/api/v1/files/handle/` to extract the `s3://` URI.
  2. The user then posts a specialized schema mapping the `document_url` to a `provider` id at `/api/v1/users/provider-documents/` (which *also* expects JWT constraints).
- **SDK Solution:** Built an abstraction `.upload_and_associate_document()` to bridge this workflow securely underneath a single execution wrapper while preserving accurate typing semantics!
