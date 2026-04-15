# Authentication

The Assured Platform uses two distinct authentication mechanisms. The SDK handles both transparently, but understanding when each is used helps when debugging or extending the client.

## Dual Auth Model

```
┌──────────────────────────────────────────────┐
│               AssuredClient                  │
│                                              │
│  ┌─────────────┐      ┌──────────────────┐   │
│  │  API Key     │      │  JWT (Bearer)    │   │
│  │  x-api-key   │      │  Authorization   │   │
│  │              │      │                  │   │
│  │  • Providers │      │  • File uploads  │   │
│  │  • Profiles  │      │  • Presigned URLs│   │
│  │  • Licenses  │      │  • SSN updates   │   │
│  │  • Creds     │      │  • Documents     │   │
│  │  • Enrollment│      │                  │   │
│  └─────────────┘      └──────────────────┘   │
└──────────────────────────────────────────────┘
```

### API Key Authentication (Default)

Most Assured endpoints accept a static API key passed via the `x-api-key` header. This is configured through the `ASSURED_API_KEY` environment variable and is injected automatically on every request.

### JWT Bearer Authentication

Certain undocumented endpoints — primarily those dealing with file storage, SSN encryption, and document associations — reject the API key and require a session JWT obtained via the login endpoint.

## How JWT Caching Works

The SDK implements **lazy, one-time JWT acquisition**:

1. On the first call to a JWT-protected method, the client automatically calls `/api/v1/users/login/` using `ASSURED_USER` and `ASSURED_PASS`.
2. The returned access token is cached in memory for the lifetime of the client session.
3. Subsequent JWT-protected calls reuse the cached token — no redundant login requests.

```python
async with AssuredClient() as client:
    # First JWT-protected call triggers automatic login
    file = await client.files.upload(content, "doc.pdf")

    # Second call reuses the cached JWT — no extra login
    url = await client.files.presign_url(file.file_url)
```

!!! warning "Token Expiry"
    The cached JWT is not automatically refreshed. If your session runs longer than the token's TTL (typically ~2.8 hours based on observed behavior), you may need to create a new `AssuredClient` instance.

## Identifying JWT-Protected Methods

In the SDK source, any method that requires JWT authentication passes `requires_jwt=True` to the internal HTTP helpers:

```python
# Internal pattern — you don't call this directly
resp = await self._client._post(path, json=payload, requires_jwt=True)
```

The following resource methods use JWT authentication:

| Resource | Method |
|---|---|
| `client.files` | `upload()`, `presign_url()` |
| `client.provider_profile` | `create_document()`, `upload_and_associate_document()` |

## Password Resets

The SDK also supports triggering password reset emails for providers:

```python
await client.users.password_reset("provider@example.com")
```

This is the mechanism used to send initial credentials to newly onboarded providers.
