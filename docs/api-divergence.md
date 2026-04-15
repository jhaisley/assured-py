# API Divergence — Spec vs Reality

This document outlines the known discrepancies between the official OpenAPI specification and the actual operational behavior of the production Assured Platform API.

!!! warning
    These endpoints and payloads deviate from the documented spec. The `assured-py` SDK has been built to support **actual** production behavior, superseding the official OpenAPI schema in these cases.

## 1. Provider Personal Info

**Spec:** Undocumented entirely in the OpenAPI spec.

**Reality:** The API exposes comprehensive GET and PATCH endpoints for managing a provider's primary demographic, descriptive, and background context.

- **Methods:** `GET` and `PATCH` on `/api/v1/users/provider-personal-info/{profile_id}/`
- **Payload:** 55 fields encompassing demographics (name, DOB, SSN, NPI, CAQH ID), residency addresses, correspondence addresses, practice settings, languages, ECFMG status, visa/citizenship details, and military service records.
- **Quirk:** The API requires the *complete* model payload on `PATCH` — omitting unmodified fields triggers `HTTP 400`. The SDK's `update_personal_info` handles this automatically via fetch-merge-patch.

## 2. Provider Employment Endpoints

**Spec:** Documented as `GET / POST / PATCH / DELETE` on `/api/v1/users/provider-employments/`.

**Reality:** The platform has silently migrated to a `v1` endpoint with a drastically different schema.

- **Endpoint:** `/api/v1/users/provider-employment-v1/` (not the documented path)
- **Deprecated fields:** `is_current` → `currently_employed`, `reason_for_leaving` → `reason_for_discontinuance`
- **New required fields:** `type`, `gap_explanation`, `address`, `city`, `state`, `country`, `zip_code`, `phone_number`, `email_address`, `contact_information`, `document`

## 3. Provider Education Endpoints

**Spec:** Simple model with `institution_name`, `degree`, `start_date`, `end_date`.

**Reality:** Requires a much richer location-oriented schema.

- **Deprecated fields:** `institution_name` superseded by `name`
- **New fields:** `city`, `state`, `country`, `is_primary`, `address_street_1`, `address_street_2`, `postal_code`

## 4. Provider Account vs Provider Profile IDs

**Spec:** Implies a generic "Provider ID" across routes.

**Reality:** The API is highly sensitive to the distinction between Account and Profile IDs.

| ID Type | Usage |
|---|---|
| **Account ID** | `providers-list/`, invite endpoints |
| **Profile ID** | All `provider_profile` domains (personal info, certs, licenses, insurance, etc.) |

Mixing them causes `404` or `422` errors. The SDK provides `client.providers.get_profile_id(account_id)` to bridge this gap.

## 5. Encrypted SSN Endpoint

**Spec:** Not documented.

**Reality:** SSNs must be submitted as symmetrically encrypted tokens.

- **Endpoint:** `PATCH /api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{profile_id}/`
- **Auth:** Rejects API keys — requires `Authorization: Bearer {jwt}`
- **Encryption:** AES-256-CTR with a SHA-256 hash of the JWT as the symmetric key. A random 16-byte IV is prepended before Base64 encoding.

## 6. JWT Generation (Login)

**Spec:** No documented endpoint for acquiring session JWTs.

**Reality:** The frontend uses an undocumented login endpoint.

- **Endpoint:** `POST /api/v1/users/login/`
- **Payload:** `{"email": "...", "password": "...", "remember": true}`
- **SDK Solution:** Lazy JWT caching — credentials from `ASSURED_USER` / `ASSURED_PASS` are used to acquire a token on first need, then cached for the session lifetime.

## 7. File Uploads and Presigned URLs

**Spec:** Generic REST models.

**Reality:** Custom AWS storage APIs driven through the Django interface.

- **Upload:** `POST /api/v1/files/handle/` with `multipart/form-data` (JWT required). Returns an `s3://` URI.
- **Presigned URLs:** `POST /api/v1/files/presign-s3-url/presign_s3_url/` exchanges the `s3://` path for a time-limited public URL.
- **Accepted formats:** PDF, PNG, JPEG only.

## 8. Provider Document Associations

**Spec:** Documents loosely grouped without explicit multi-stage processes.

**Reality:** Two-step process:

1. Upload raw file via `/api/v1/files/handle/` → extract `s3://` URI
2. POST to `/api/v1/users/provider-documents/` mapping the URI to a provider (also JWT-protected)

The SDK's `upload_and_associate_document()` abstracts this into a single call.

## 9. Users List Endpoint

**Spec:** Documented as `GET /api/v1/users/users-list/`.

**Reality:** The documented endpoint is dead (returns errors). The platform has silently migrated to an external-facing variant.

- **Working endpoint:** `GET /api/v1/users/external-users-list/`
- **Response:** Same paginated structure (`count`, `next`, `previous`, `results`), same core fields.
- **New fields added:** `invited_at`, `source_of_joining`, `client` (UUID), `client_name` — not present in the original spec.
- **SDK Solution:** The SDK points to the working endpoint and includes the additional fields on the `User` model.
