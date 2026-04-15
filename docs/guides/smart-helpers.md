# Smart Helpers

The Assured API has numerous quirks that make raw HTTP interaction painful — mismatched IDs, multi-stage workflows, encrypted payloads, and endpoints that demand complete models for partial updates. The SDK abstracts all of this behind simple, intuitive methods.

## Provider ID Resolution

The Assured API uses **two distinct UUIDs** per provider — an Account ID and a Profile ID. Most profile endpoints require the Profile ID, but you'll typically start with just an Account ID.

!!! warning "A common pitfall"
    Passing an Account ID to a profile endpoint (certifications, licenses, personal info, etc.) silently returns `404` or `422`. The API gives no helpful error message.

The SDK provides `get_profile_id()` to handle the translation:

```python
# You have an account ID from a provider list
account_id = "f67a6eca-5a59-4d91-92af-0e230b350e65"

# Resolve it to the profile ID needed by profile endpoints
profile_id = await client.providers.get_profile_id(account_id)

# Now use it for profile operations
info = await client.provider_profile.get_personal_info(profile_id)
certs = await client.provider_profile.list_certifications_all(provider=profile_id)
licenses = await client.provider_profile.list_licenses_all(provider=profile_id)
```

## NPI Lookup with Caching

Assured doesn't offer a native NPI search. The SDK pulls the full provider list, indexes it by NPI, and caches the result for **5 minutes**:

```python
provider = await client.providers.get_by_npi("1234567890")
print(f"{provider.full_name} — {provider.email}")

# Subsequent calls within 5 minutes use the cache — zero API calls
another = await client.providers.get_by_npi("0987654321")
```

## Fetch-Merge-Patch for Personal Info

The Assured API requires the **complete model** on every `PATCH` to personal info — omitting unchanged fields causes `400` errors. The SDK handles this automatically:

```python
from assured.models.provider_profile import ProviderPersonalInfoUpdate

# Only specify the fields you want to change
update = ProviderPersonalInfoUpdate(
    correspondence_email="new-email@example.com",
    home_phone="555-0123",
)

# The SDK automatically:
# 1. Fetches the current full record
# 2. Merges your changes on top
# 3. Sends the complete payload
result = await client.provider_profile.update_personal_info(profile_id, update)
```

## SSN Encryption

The platform requires SSNs to be submitted as AES-256-CTR encrypted tokens rather than plaintext. The SDK handles the full encryption pipeline:

```python
await client.provider_profile.update_ssn(
    provider_id=profile_id,
    ssn="123-45-6789",
    jwt=jwt_token,  # Used as the encryption key source
)
```

Under the hood, the SDK:

1. Strips formatting from the SSN
2. Derives an AES-256 key from the SHA-256 hash of the JWT
3. Generates a random 16-byte IV
4. Encrypts with AES-256-CTR
5. Prepends the IV and Base64-encodes the result
6. Sends via the undocumented encrypted SSN endpoint

## Two-Stage File Upload

Associating a document with a provider requires uploading to S3 first, then linking the result. The SDK wraps both steps:

```python
with open("license.pdf", "rb") as f:
    doc = await client.provider_profile.upload_and_associate_document(
        provider_id=profile_id,
        file_content=f.read(),
        filename="license.pdf",
        document_name="State Medical License",
        document_type="License",
    )
```

The SDK also validates file format before making any network requests — only `.pdf`, `.png`, `.jpg`, and `.jpeg` are accepted.

See the [File Uploads Guide](file-uploads.md) for full details.

## Automatic JWT Session Management

Several undocumented endpoints reject the standard API key and require a Bearer JWT. The SDK handles this transparently:

- **Lazy acquisition** — The JWT is only fetched on the first call that needs it
- **Session caching** — Subsequent calls reuse the cached token
- **Zero configuration** — Just set `ASSURED_USER` and `ASSURED_PASS` in your `.env`

You never need to think about which auth method a particular endpoint uses.

See the [Authentication Guide](authentication.md) for the full breakdown.

## Auto-Pagination

Every list resource provides three access patterns. The SDK handles following `next` links automatically:

```python
# Single page
page = await client.providers.list(limit=10)

# All records (auto-paginated)
all_records = await client.providers.list_all()

# Directly as a DataFrame
df = await client.providers.list_df()
```

See the [Pagination Guide](pagination.md) for the complete list of available methods.
