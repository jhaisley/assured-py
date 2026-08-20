# Assured Platform API — Spec vs Reality

This document outlines the known discrepancies between the official OpenAPI specification (`Assured Platform API.json`) and the actual operational behavior of the production Assured Platform API as implemented in the `assured` SDK.

A recent spec update (58 → 94 endpoints) officially documented several endpoints this SDK had previously reverse-engineered. Those items now live under **Formerly undocumented — now in the official spec** below; the behavioral quirks recorded there (encryption, JWT-only auth, optional-vs-nullable PATCH fields) still hold in production. Section numbers are historical and stable — SDK docstrings reference them by number — so sections keep their original numbers when they move between groups.

---

> [!WARNING]
> The endpoints and payloads under **Active divergences** deviate from the documented spec. The `assured` SDK has been built to support **actual** production behavior, superseding the official OpenAPI schema in these cases.

## Active divergences

### 4. Provider Account vs Provider Profile IDs

**Spec:** Often implies a generic "Provider ID" is passed across routes.
**Reality:** The API is highly sensitive to the distinction between a Provider Account and a Provider Profile.

| ID Type | Usage |
|---|---|
| **Provider Account ID** | The core identity record (UUID), passed to the list and invite endpoints. |
| **Provider Profile ID** | A separate UUID 1:1 linked to the account, used by nearly all `provider_profile` domains (personal info, certifications, licenses, insurance, etc.) and the org-joining-date endpoints. |

Mixing them up causes the API to fail with `404` or `422`. The SDK provides a dedicated resolution helper, `client.providers.get_profile_id(account_id)`, to bridge this gap automatically.

### 7. File Uploads and Presigned URLs

**Spec:** Still absent — the new spec documents no `/api/v1/files/` routes at all.
**Reality:** The entire document handling subsystem is built on heavily customized AWS storage APIs driven through the Assured Django interface.

- **Storage Extraction:** Files must be uploaded to `/api/v1/files/handle/` using a raw `multipart/form-data` payload containing a UUID `name` key, and the binary data under `file`. This endpoint specifically enforces JWT Bearer authentication. It returns an `s3://` object reference (`file_url`).
- **Temporary Access:** Due to S3 protections, URLs cannot be exposed safely. The SDK invokes `/api/v1/files/presign-s3-url/presign_s3_url/`, feeding it back the `s3://` path, which brokers a limited-time publicly accessible URL.
- **Accepted formats:** PDF, PNG, JPEG only.

### 8. Provider Document Associations

**Spec:** `GET` / `POST /api/v1/users/provider-documents/` is now officially documented — but under the standard API-key security scheme, with no mention of the upload flow it depends on.
**Reality:** Linking an actual file binary to a Provider Profile is a two-step process, and both steps require JWT Bearer authentication in production.

- **Process:**
  1. The user must first process the raw file via the JWT-restricted (and still undocumented) route `/api/v1/files/handle/` to extract the `s3://` URI (see section 7).
  2. The user then posts a specialized schema mapping the `document_url` to a `provider` id at `/api/v1/users/provider-documents/` — which, despite the spec's API-key auth claim, *also* expects JWT constraints in production.
- **SDK Solution:** Built an abstraction `.upload_and_associate_document()` to bridge this workflow securely underneath a single execution wrapper while preserving accurate typing semantics!

### 9. Users List Endpoint

**Spec:** Originally documented as `GET /api/v1/users/users-list/`; that route has now been **removed from the spec entirely** (see *Removed from the spec* below). Its working replacement remains undocumented.
**Reality:** The documented endpoint was dead (returned errors) long before its removal. The platform silently migrated to an external-facing variant.

- **Working Endpoint:** `GET /api/v1/users/external-users-list/` — still absent from the new spec.
- **Response:** Same paginated structure (`count`, `next`, `previous`, `results`), same core user fields.
- **New Fields:** `invited_at`, `source_of_joining`, `client` (UUID), `client_name` — not present in the original spec.
- **SDK Solution:** The SDK points to the working endpoint and includes the additional fields on the `User` model automatically. (The new spec does add a documented `GET /api/v1/users/user-list-slim/`, exposed as `client.users.list_slim()`, but it returns a reduced field set and is not a replacement for the external list.)

### 10. Password Reset

**Spec:** Not documented. The spec offers only `POST /api/v1/users/change-password/`, which requires knowing the current password.
**Reality:** The frontend triggers password-reset emails through an undocumented endpoint.

- **Endpoint:** `POST /api/v1/users/password-reset/` with `{"email": "..."}`.
- **SDK Solution:** Exposed as `client.users.password_reset(email)`.

### 11. Optional-but-not-nullable request fields

**Spec:** `POST /api/v1/users/create-providers/` requires only `email`, `first_name` and `last_name`. `client`, `document_url` and `document_type` are optional.
**Reality:** Optional means *omit the key*, never *send `null`*. Those three are typed as plain (non-nullable) strings, so passing `null` fails with `HTTP 400 — "This field may not be null."` on all three at once, even though the spec calls them optional. Verified against production 2026-08-20.

- **SDK Solution:** `providers.create()` serializes with `exclude_none=True`, so unset fields are omitted. `client` is assigned server-side from the caller's org when absent.
- **Same shape elsewhere:** `providers.invite()` and `providers.import_with_caqh()` now also serialize with `exclude_none=True` for the same reason. Neither has been exercised against production (both have outward-facing side effects — `invite` sends email to the provider), but omitting unset keys matches the verified semantics of their sibling `create()` and is what the pre-update payloads (before these optional fields existed) always did.
- **Related:** Section 1 documents the same optional-vs-nullable confusion on `provider-personal-info`, where it is considerably more damaging.

## Formerly undocumented — now in the official spec

The spec update brought the endpoints below into the official OpenAPI document. They are no longer divergences in the "endpoint does not exist on paper" sense, but the behavioral quirks noted here **still apply in production** and remain unspecified.

### 1. Provider Personal Info (`provider-personal-info`)

**Spec (updated):** `GET` and `PATCH /api/v1/users/provider-personal-info/{profile_id}/` are now documented, with a 67-field schema encompassing demographics (name, DOB, NPI, CAQH ID), residency addresses, correspondence addresses, practice settings, languages, ECFMG status, visa/citizenship details, and military service records.
**Standing quirk:** The spec models `PATCH` as a standard partial update (operationId `partialUpdateProviderPersonalInfo`, no required fields). Production diverges in two ways — but *not* in the way previously recorded here.

- **Nulls are rejected, not required.** This document previously claimed the API demands the complete model and that `null` must be sent rather than omitting a key. That is backwards. Most fields are non-nullable on the way in, so an explicit `null` draws `HTTP 400 — "This field may not be null."` A genuinely partial payload of three fields is accepted. Verified against production 2026-08-20.
- **Consequence for new providers.** A profile fresh from `create-providers` is almost entirely `null`, so a fetch-merge-patch that echoed those nulls back failed with **23 simultaneous** "may not be null" errors, making the create → populate flow impossible to complete. `update_personal_info` now drops null-valued fields from the merged payload; an explicit `None` on the *update* model is still sent, so clearing a field on purpose still works.
- **Citizenship is required on every write.** Independent of what you are setting, the endpoint rejects any `PATCH` leaving citizenship unset: `"Citizenship country is required"` and `"Visa number is required for non-US citizens"`. The first write to a new profile must include `us_citizen` and `citizenship_country`. Nothing in the spec indicates this.

The SDK still strips the spec's response-only fields from the merged payload — including `ssn`, whose fetched value is masked/ciphertext in production and must never be echoed back; SSN changes go through the dedicated encrypted endpoint in section 5.

### 2. Provider Employment Endpoints

**Spec (updated):** `GET` / `POST /api/v1/users/provider-employment-v1/` — the endpoint the platform silently migrated to, and the one this SDK already targeted — is now the officially documented route. The legacy `/api/v1/users/provider-employments/` has been removed from the spec (see *Removed from the spec* below).
**Standing notes:** The documented schema matches what the SDK reverse-engineered (`currently_employed`, `reason_for_discontinuance`, address/contact fields, `gap_explanation`, `document`). The SDK's `Employment` and `EmploymentCreate` models retain the older schema's fields (`position`, `type`, `is_current`, `reason_for_leaving`) as legacy extras for backward compatibility; they are absent from the official schema.

### 3. Provider Education Endpoints

**Spec (updated):** The education schema has caught up with reality: `name`, `city`, `state`, `country`, `is_primary`, `address_street_1`, `address_street_2`, `postal_code`, and `document` are all now documented on `/api/v1/users/provider-education/`.
**Standing notes:** `institution_name` — the old spec's field — is retained on the SDK `Education` models for legacy use only; the official schema uses `name`.

### 5. Encrypted SSN Endpoint

**Spec (updated):** `GET` and `PATCH /api/v1/users/retrieve-update-provider-ssn-sym-encrypted/{profile_id}/` are now documented — but as a plain `{"ssn": "<string>"}` payload under the standard API-key security scheme.
**Standing quirks (both undocumented):**

- **Authentication:** Production rejects standard API Keys on this endpoint and strictly requires `Authorization: Bearer {jwt}` headers using a valid session JWT token.
- **Payload & Encryption:** The `ssn` value must be a Base64-encoded ciphertext using the `AES-256-CTR` standard. The symmetric key is dynamically generated via a `SHA256` hash of the provided JWT token, and a random 16-byte `IV` is prefixed against the ciphertext before Base64 encoding. The `GET` likewise returns ciphertext, not plaintext.

### 6. JWT Generation (Login)

**Spec (updated):** `POST /api/v1/users/login/` is now documented (operationId `userLogin`), including the full response payload (`data` with `jwt.access` / `jwt.refresh`, `msg`, and `extra_data` carrying client/MFA/feature-flag info).
**Standing quirk:** The `remember` flag the frontend sends is accepted by production but absent from the documented request schema (which lists only `email` and `password`).

- **SDK Solution:** `await client.users.login(email, password)` still returns just the access token and feeds the client's lazy JWT cache (credentials pulled via `pydantic-settings` from `ASSURED_USER` and `ASSURED_PASS`, automating JWT injection when standard API Key authentication isn't enough). The new `client.users.login_full()` returns the full documented payload.

## Removed from the spec

The spec update also deleted endpoints outright:

- `GET /api/v1/users/users-list/` — was already dead in production (see section 9); the SDK never depended on it.
- `GET` / `POST /api/v1/users/provider-employments/` — superseded by `provider-employment-v1` (see section 2); the SDK already targeted the v1 route.
