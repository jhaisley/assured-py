# Payer Enrollment

Covers enrollment requests (create, detail, status updates, timeline), existing enrollments,
health plans, active enrollments, and Operations Analyst (OA) assignment.

Notable methods:

- `get_request_detail(request_id)` — full detail of an enrollment request.
- `update_request_status(request_id, data)` — cancel or otherwise change a request's status.
- `list_enrollment_timeline()` / `_all()` / `_df()` — enrollment request timeline entries.
- `add_existing_group_enrollment(data)` / `add_existing_provider_enrollment(data)` — record
  enrollments that already exist with a payer.
- `bulk_oa_assignment(data)` — bulk-assign OAs to enrollment requests (round-robin).
- `list_reassignment_selectable_oa_users(enrollment_request)` — OA users selectable for
  reassignment on a request.

## Resource

::: assured.resources.payer_enrollment.PayerEnrollmentResource

## Models

::: assured.models.payer_enrollment.GroupEnrollmentRequestCreate

::: assured.models.payer_enrollment.ProviderEnrollmentRequestCreate

::: assured.models.payer_enrollment.ExistingProviderEnrollmentCreate

::: assured.models.payer_enrollment.ExistingProviderEnrollment

::: assured.models.payer_enrollment.ExistingGroupEnrollmentCreate

::: assured.models.payer_enrollment.ExistingGroupEnrollment

::: assured.models.payer_enrollment.HealthPlan

::: assured.models.payer_enrollment.EnrollmentRequest

::: assured.models.payer_enrollment.EnrollmentRequestDetail

::: assured.models.payer_enrollment.GroupProviderRef

::: assured.models.payer_enrollment.EnrollmentRequestStatusUpdate

::: assured.models.payer_enrollment.EnrollmentTimelineEntry

::: assured.models.payer_enrollment.EnrollmentTimelineParams

::: assured.models.payer_enrollment.SelectableOaUser

::: assured.models.payer_enrollment.BulkOaAssignment

::: assured.models.payer_enrollment.ActiveEnrollment

::: assured.models.payer_enrollment.EnrollmentListParams

::: assured.models.payer_enrollment.ActiveEnrollmentListParams
