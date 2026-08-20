# API Divergence — Spec vs Reality

This document outlines the known discrepancies between the official OpenAPI specification and the actual operational behavior of the production Assured Platform API.

A recent spec update (58 → 94 endpoints) officially documented several endpoints this SDK had previously reverse-engineered. Those items now live under **Formerly undocumented — now in the official spec** below; the behavioral quirks recorded there (encryption, JWT-only auth, full-payload PATCH) still hold in production. Section numbers are historical and stable — SDK docstrings reference them by number — so sections keep their original numbers when they move between groups.

!!! warning
    The endpoints and payloads under **Active divergences** deviate from the documented spec. The `assured-py` SDK has been built to support **actual** production behavior, superseding the official OpenAPI schema in these cases.

## Active divergences

### 4. Provider Account vs Provider Profile IDs

**Spec:** Implies a generic "Provider ID" across routes.

**Reality:** The API is highly sensitive to the distinction between Account and Profile IDs.

| ID Type | Usage |
|---|---|
| **Provider Account ID** | The core identity record (UUID), passed to the list and invite endpoints. |
| **Provider Profile ID** | A separate UUID 1:1 linked to the account, used by nearly all `provider_profile` domains (personal info, certifications, licenses, insurance, etc.) and the org-joining-date endpoints. |

Mixing them causes `404` or `422` errors. The SDK provides `client.providers.get_profile_id(account_id)` to bridge this gap.

### 7. File Uploads and Presigned URLs

**Spec:** Still absent — the new spec documents no `/api/v1/files/` routes at all.

**Reality:** Custom AWS storage APIs driven through the Django interface.

- **Upload:** `POST /api/v1/files/handle/` with `multipart/form-data` (JWT required) — a UUID `name` key plus the binary data under `file`. Returns an `s3://` URI (`file_url`).
- **Presigned URLs:** `POST /api/v1/files/presign-s3-url/presign_s3_url/` exchanges the `s3://` path for a time-limited public URL.
- **Accepted formats:** PDF, PNG, JPEG only.

### 8. Provider Document Associations

**Spec:** `GET` / `POST /api/v1/users/provider-documents/` is now officially documented — but under the standard API-key security scheme, with no mention of the upload flow it depends on.

**Reality:** Linking a file binary to a Provider Profile is a two-step process, and both steps require JWT Bearer authentication in production:

1. Upload the raw file via the JWT-restricted (and still undocumented) `/api/v1/files/handle/` → extract the `s3://` URI (see section 7)
2. POST to `/api/v1/users/provider-documents/` mapping the URI to a provider — which, despite the spec's API-key auth claim, is *also* JWT-protected in production

The SDK's `upload_and_associate_document()` abstracts this into a single call.

### 9. Users List Endpoint

**Spec:** Originally documented as `GET /api/v1/users/users-list/`; that route has now been **removed from the spec entirely** (see *Removed from the spec* below). Its working replacement remains undocumented.

**Reality:** The documented endpoint was dead (returned errors) long before its removal. The platform silently migrated to an external-facing variant.

- **Working endpoint:** `GET /api/v1/users/external-users-list/` — still absent from the new spec.
- **Response:** Same paginated structure (`count`, `next`, `previous`, `results`), same core fields.
- **New fields added:** `invited_at`, `source_of_joining`, `client` (UUID), `client_name` — not present in the original spec.
- **SDK Solution:** The SDK points to the working endpoint and includes the additional fields on the `User` model. (The new spec does add a documented `GET /api/v1/users/user-list-slim/`, exposed as `client.users.list_slim()`, but it returns a reduced field set and is not a replacement for the external list.)

### 10. Password Reset

**Spec:** Not documented. The spec offers only `POST /api/v1/users/change-password/`, which requires knowing the current password.

**Reality:** The frontend triggers password-reset emails through an undocumented endpoint.

- **Endpoint:** `POST /api/v1/users/password-reset/` with `{"email": "..."}`.
- **SDK Solution:** Exposed as `client.users.password_reset(email)`.

## Formerly undocumented — now in the official spec

The spec update brought the endpoints below into the official OpenAPI document. They are no longer divergences in the "endpoint does not exist on paper" sense, but the behavioral quirks noted here **still apply in production** and remain unspecified.

### 1. Provider Personal Info

**Spec (updated):** `GET` and `PATCH` on `/api/v1/users/provider-personal-info/{profile_id}/` are now documented, with a 67-field schema encompassing demographics (name, DOB, NPI, CAQH ID), residency addresses, correspondence addresses, practice settings, languages, ECFMG status, visa/citizenship details, and military service records.

**Standing quirk:** The spec models `PATCH` as a standard partial update (operationId `partialUpdateProviderPersonalInfo`, no required fields). Production disagrees: the API still requires the *complete* model payload — omitting unmodified fields triggers `HTTP 400`, and `null` must be sent explicitly for nullable fields rather than omitting the key. This divergence stands; the SDK's `update_personal_info` continues to handle it automatically via fetch-merge-patch (and now also strips the spec's response-only fields from the merged payload — including `ssn`, whose fetched value is masked/ciphertext in production and must never be echoed back; SSN changes go through the dedicated encrypted endpoint in section 5).

### 2. Provider Employment Endpoints

**Spec (updated):** `GET` / `POST /api/v1/users/provider-employment-v1/` — the endpoint the platform silently migrated to, and the one this SDK already targeted — is now the officially documented route. The legacy `/api/v1/users/provider-employments/` has been removed from the spec (see *Removed from the spec* below).

**Standing notes:** The documented schema matches what the SDK reverse-engineered (`currently_employed`, `reason_for_discontinuance`, address/contact fields, `gap_explanation`, `document`). The SDK's `Employment` and `EmploymentCreate` models retain the older schema's fields (`position`, `type`, `is_current`, `reason_for_leaving`) as legacy extras for backward compatibility; they are absent from the official schema.

### 3. Provider Education Endpoints

**Spec (updated):** The education schema has caught up with reality: `name`, `city`, `state`, `country`, `is_primary`, `address_street_1`, `address_street_2`, `postal_code`, and `document` are all now documented on `/api/v1/users/provider-education/`.

**Standing notes:** `institution_name` — the old spec's field — is retained on the SDK `Education` models for legacy use only; the official schema uses `name`.

### 5. Encrypted SSN Endpoint

**Spec (updated):** `GET` and `PATCH` on `/api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{profile_id}/` are now documented — but as a plain `{"ssn": "<string>"}` payload under the standard API-key security scheme.

**Standing quirks (both undocumented):**

- **Auth:** Production rejects API keys on this endpoint — requires `Authorization: Bearer {jwt}`.
- **Encryption:** The `ssn` value must be a Base64-encoded AES-256-CTR ciphertext with a SHA-256 hash of the JWT as the symmetric key. A random 16-byte IV is prepended before Base64 encoding. The `GET` likewise returns ciphertext, not plaintext.

### 6. JWT Generation (Login)

**Spec (updated):** `POST /api/v1/users/login/` is now documented (operationId `userLogin`), including the full response payload (`data` with `jwt.access` / `jwt.refresh`, `msg`, and `extra_data` carrying client/MFA/feature-flag info).

**Standing quirk:** The `remember` flag the frontend sends is accepted by production but absent from the documented request schema (which lists only `email` and `password`).

- **SDK Solution:** Lazy JWT caching — credentials from `ASSURED_USER` / `ASSURED_PASS` are used to acquire a token on first need, then cached for the session lifetime. `client.users.login()` still returns just the access token; the new `client.users.login_full()` returns the full documented payload.

## Removed from the spec

The spec update also deleted endpoints outright:

- `GET /api/v1/users/users-list/` — was already dead in production (see section 9); the SDK never depended on it.
- `GET` / `POST /api/v1/users/provider-employments/` — superseded by `provider-employment-v1` (see section 2); the SDK already targeted the v1 route.
