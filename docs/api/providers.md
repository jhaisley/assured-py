# Providers

Provider account management: listing/filtering providers (including the new
`client`, `client_in` and `is_active` filters), inviting and creating
providers, CAQH imports (single-provider import and CAQH import requests),
practice-location association, and the provider organization joining date
endpoints (`get_org_joining_date` / `update_org_joining_date` — these take the
provider *profile* ID, not the account ID).

## Resource

::: assured.resources.providers.ProvidersResource

## Models

::: assured.models.providers.Provider

::: assured.models.providers.ProviderCreate

::: assured.models.providers.ProviderCreateResponse

::: assured.models.providers.ProviderInvite

::: assured.models.providers.ProviderCAQHImport

::: assured.models.providers.ProviderListParams

::: assured.models.providers.CaqhImportRequest

::: assured.models.providers.CaqhImportRequestCreate

::: assured.models.providers.CaqhImportRequestListParams

::: assured.models.providers.ProviderOrgJoiningDate
