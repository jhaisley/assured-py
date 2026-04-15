# Payer Enrollment

The SDK provides full coverage of the Assured Payer Enrollment subsystem — health plan lookups, enrollment requests, active enrollment management, and adding existing provider enrollments.

## Health Plans

List available health plans with optional search and state filtering:

```python
# Get all health plans
plans = await client.payer_enrollment.list_health_plans_all()

# Search by name
plans = await client.payer_enrollment.list_health_plans_all(search="Anthem")

# As a DataFrame
df = await client.payer_enrollment.list_health_plans_df()
```

## Enrollment Requests

Create and track enrollment requests:

```python
from assured.models.payer_enrollment import ProviderEnrollmentRequestCreate

# Create an enrollment request
request = ProviderEnrollmentRequestCreate(
    provider="provider-uuid",
    health_plan="health-plan-uuid",
    practice_location="location-uuid",
    tax_entity="tax-entity-uuid",
    effective_date="2025-01-01",
)
result = await client.payer_enrollment.create_provider_enrollment(request)

# List all enrollment requests
requests = await client.payer_enrollment.list_enrollment_requests_all()
```

## Active Enrollments

Query existing active enrollments:

```python
# List all active enrollments
active = await client.payer_enrollment.list_active_enrollments_all()

# As a DataFrame for analysis
df = await client.payer_enrollment.list_active_enrollments_df()
```

## Adding Existing Provider Enrollments

When a provider already has an active enrollment with a payer (established outside the platform), you can record it using `add_existing_provider_enrollment`:

```python
from assured.models.payer_enrollment import ExistingProviderEnrollmentCreate

enrollment = ExistingProviderEnrollmentCreate(
    provider="provider-uuid",
    tax_entity="tax-entity-uuid",
    state="IN",
    health_plan="health-plan-uuid",
    lobs=["Traditional Medicaid"],
    primary_practice_location="location-uuid",
    par_status="LINKED",
    new_health_plan_id="300017810",
    effective_date="2024-12-01",
    no_re_validation_date=True,
    no_proof_of_enrollment=True,
    notes="BCBA",
)

result = await client.payer_enrollment.add_existing_provider_enrollment(enrollment)
print(f"Created enrollment: {result.id}")
```

### Payload Fields

| Field | Type | Description |
|---|---|---|
| `provider` | `str` | Provider account UUID |
| `tax_entity` | `str` | Tax entity UUID |
| `state` | `str` | Two-letter state code |
| `health_plan` | `str` | Health plan UUID |
| `lobs` | `list[str]` | Lines of business (e.g., `["Traditional Medicaid"]`) |
| `primary_practice_location` | `str` | Primary practice location UUID |
| `par_status` | `str` | Participation status (e.g., `"LINKED"`) |
| `effective_date` | `str` | Effective date in `YYYY-MM-DD` format |
| `new_health_plan_id` | `str` | The payer-assigned provider ID |
| `no_re_validation_date` | `bool` | Whether re-validation date is not applicable |
| `no_proof_of_enrollment` | `bool` | Whether proof of enrollment is not available |
| `notes` | `str` | Free-text notes |

## Group Enrollment Requests

For group-level enrollments:

```python
from assured.models.payer_enrollment import GroupEnrollmentRequestCreate

group = GroupEnrollmentRequestCreate(
    health_plan="health-plan-uuid",
    practice_location="location-uuid",
    tax_entity="tax-entity-uuid",
    effective_date="2025-01-01",
)
result = await client.payer_enrollment.create_group_enrollment(group)
```
