# Pagination & DataFrames

Every list-based resource in the SDK provides three access patterns to handle Assured's paginated API responses.

## The Three Patterns

### `list()` — Single Page

Returns one page of results. Useful when you need fine-grained control over pagination or only need the first batch.

```python
# Get the first page (default page size)
providers = await client.providers.list()

# Control page size and offset
providers = await client.providers.list(limit=10, offset=20)
```

### `list_all()` — All Records

Automatically follows `next` pagination links and returns every record as a flat list of typed Pydantic models.

```python
# Fetch all providers across all pages
all_providers = await client.providers.list_all()
print(f"Total: {len(all_providers)} providers")
```

### `list_df()` — pandas DataFrame

Same auto-pagination as `list_all()`, but returns results as a `pandas.DataFrame` — ideal for analysis, filtering, and export.

```python
df = await client.providers.list_df()

# Filter, sort, export
active = df[df["is_active"] == True]
active.to_csv("active_providers.csv", index=False)
```

## Available on Every Resource

All three patterns are available across every list-capable resource:

| Resource | Methods |
|---|---|
| `client.providers` | `list()`, `list_all()`, `list_df()` |
| `client.provider_profile` | `list_certifications()`, `list_certifications_all()`, `list_certifications_df()` |
| | `list_licenses()`, `list_licenses_all()`, `list_licenses_df()` |
| | `list_dea()`, `list_dea_all()`, `list_dea_df()` |
| | `list_cds()`, `list_cds_all()`, `list_cds_df()` |
| | `list_medicaid()`, `list_medicaid_all()`, `list_medicaid_df()` |
| | `list_medicare()`, `list_medicare_all()`, `list_medicare_df()` |
| | `list_employments()`, `list_employments_all()`, `list_employments_df()` |
| | `list_gap_history()`, `list_gap_history_all()`, `list_gap_history_df()` |
| | `list_education()`, `list_education_all()`, `list_education_df()` |
| | `list_training()`, `list_training_all()`, `list_training_df()` |
| | `list_insurance()`, `list_insurance_all()`, `list_insurance_df()` |
| `client.credentialing` | `list_requests()`, `list_requests_all()`, `list_requests_df()` |
| `client.payer_enrollment` | `list_health_plans()`, `list_health_plans_all()`, `list_health_plans_df()` |
| | `list_enrollment_requests()`, `list_enrollment_requests_all()`, `list_enrollment_requests_df()` |
| | `list_active_enrollments()`, `list_active_enrollments_all()`, `list_active_enrollments_df()` |
| `client.users` | `list()`, `list_all()`, `list_df()` |

## Filtering

Most list methods accept keyword arguments that map to the API's query parameters:

```python
# Filter providers by a specific provider ID
providers = await client.providers.list(
    params=ProviderListParams(id_in="some-uuid")
)

# Filter certifications by provider
certs = await client.provider_profile.list_certifications_all(
    provider="provider-profile-uuid"
)
```

## How Auto-Pagination Works

Under the hood, `list_all()` and `list_df()` call the client's `_get_all_pages()` method, which:

1. Makes an initial request to get the first page and `count`.
2. Checks the `next` URL in the response.
3. Continues fetching until `next` is `null`.
4. Aggregates all `results` arrays into a single flat list.

This means a resource with 500 records across 5 pages will fire 5 sequential HTTP requests automatically.

!!! tip "Performance"
    For very large datasets, consider using `list()` with explicit pagination if you only need a subset of records. `list_all()` will fetch everything, which may be slow for resources with thousands of entries.
