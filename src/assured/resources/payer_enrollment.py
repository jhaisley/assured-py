"""Payer enrollment resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.payer_enrollment import (
    ActiveEnrollment,
    ActiveEnrollmentListParams,
    BulkOaAssignment,
    EnrollmentListParams,
    EnrollmentRequest,
    EnrollmentRequestDetail,
    EnrollmentRequestStatusUpdate,
    EnrollmentTimelineEntry,
    EnrollmentTimelineParams,
    ExistingGroupEnrollment,
    ExistingGroupEnrollmentCreate,
    ExistingProviderEnrollment,
    ExistingProviderEnrollmentCreate,
    GroupEnrollmentRequestCreate,
    HealthPlan,
    ProviderEnrollmentRequestCreate,
    SelectableOaUser,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_GROUP_ENROLL_PATH = "/api/v1/payer-enrollment/group-enrollment-request/"
_PROVIDER_ENROLL_PATH = "/api/v1/payer-enrollment/provider-enrollment-request/"
_HEALTH_PLAN_PATH = "/api/v1/payer-enrollment/health-plan/"
_ENROLLMENT_LIST_PATH = "/api/v1/payer-enrollment/enrollment-request-list/"
_ENROLLMENT_DETAIL_PATH = "/api/v1/payer-enrollment/enrollment-request-detail/{id}/"
_ENROLLMENT_UPDATE_STATUS_PATH = "/api/v1/payer-enrollment/enrollment-request-update-status/{id}/"
_ENROLLMENT_TIMELINE_PATH = "/api/v1/payer-enrollment/enrollment-request-timeline/"
_ACTIVE_ENROLLMENT_PATH = "/api/v1/payer-enrollment/active-enrollment-list/"
_ADD_EXISTING_GROUP_PATH = "/api/v1/payer-enrollment/add-existing-group-enrollment/"
_ADD_EXISTING_PROVIDER_PATH = "/api/v1/payer-enrollment/add-existing-provider-enrollment/"
_BULK_OA_ASSIGNMENT_PATH = "/api/v1/payer-enrollment/self-serve/bulk-oa-assignment/"
_SELECTABLE_OA_USERS_PATH = "/api/v1/payer-enrollment/payer-enrollment-request-reassignment-selectable-oa-users-list/"


class PayerEnrollmentResource:
    """Operations on payer enrollments."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    # ---- Create ----

    async def create_group_enrollment(self, data: GroupEnrollmentRequestCreate) -> dict[str, Any]:
        return await self._client._post(_GROUP_ENROLL_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def create_provider_enrollment(self, data: ProviderEnrollmentRequestCreate) -> dict[str, Any]:
        return await self._client._post(_PROVIDER_ENROLL_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def add_existing_provider_enrollment(
        self, data: ExistingProviderEnrollmentCreate
    ) -> ExistingProviderEnrollment:
        """Add an existing provider enrollment.

        Args:
            data: The existing provider enrollment payload.

        Returns:
            The created existing provider enrollment.
        """
        resp = await self._client._post(_ADD_EXISTING_PROVIDER_PATH, json=data.model_dump(mode="json", exclude_none=False))
        return ExistingProviderEnrollment.model_validate(resp)

    async def add_existing_group_enrollment(self, data: ExistingGroupEnrollmentCreate) -> ExistingGroupEnrollment:
        """Add an existing group enrollment.

        Args:
            data: The existing group enrollment payload.

        Returns:
            The created existing group enrollment.
        """
        resp = await self._client._post(_ADD_EXISTING_GROUP_PATH, json=data.model_dump(mode="json", exclude_none=False))
        return ExistingGroupEnrollment.model_validate(resp)

    # ---- Health Plans ----

    async def list_health_plans(
        self, *, limit: int | None = None, offset: int | None = None, search: str | None = None
    ) -> list[HealthPlan]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        data = await self._client._get_page(_HEALTH_PLAN_PATH, params=params)
        return [HealthPlan.model_validate(i) for i in data.get("results", [])]

    async def list_health_plans_all(self, *, search: str | None = None) -> list[HealthPlan]:
        params: dict[str, Any] = {}
        if search is not None:
            params["search"] = search
        records = await self._client._get_all_pages(_HEALTH_PLAN_PATH, params=params)
        return [HealthPlan.model_validate(i) for i in records]

    async def list_health_plans_df(self, *, search: str | None = None) -> pd.DataFrame:
        params: dict[str, Any] = {}
        if search is not None:
            params["search"] = search
        records = await self._client._get_all_pages(_HEALTH_PLAN_PATH, params=params)
        return self._client.to_dataframe(records)

    # ---- Enrollment Requests ----

    async def list_enrollment_requests(
        self, params: EnrollmentListParams | None = None, **kwargs: Any
    ) -> list[EnrollmentRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_ENROLLMENT_LIST_PATH, params=raw_params)
        return [EnrollmentRequest.model_validate(i) for i in data.get("results", [])]

    async def list_enrollment_requests_all(
        self, params: EnrollmentListParams | None = None, **kwargs: Any
    ) -> list[EnrollmentRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ENROLLMENT_LIST_PATH, params=raw_params)
        return [EnrollmentRequest.model_validate(i) for i in records]

    async def list_enrollment_requests_df(
        self, params: EnrollmentListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ENROLLMENT_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_request_detail(self, request_id: str) -> EnrollmentRequestDetail:
        """Get the full detail of a payer enrollment request.

        Args:
            request_id: The enrollment request ID.

        Returns:
            The enrollment request detail.
        """
        data = await self._client._get(_ENROLLMENT_DETAIL_PATH.format(id=request_id))
        return EnrollmentRequestDetail.model_validate(data)

    async def update_request_status(
        self, request_id: str, data: EnrollmentRequestStatusUpdate
    ) -> dict[str, Any]:
        """Update the status of an enrollment request (e.g. cancel it).

        Args:
            request_id: The enrollment request ID.
            data: The status update payload. ``note`` is mandatory when
                ``status_reason`` is ``"OTHER"``.

        Returns:
            The raw response dict (``status`` and ``proof_of_documents``).
        """
        path = _ENROLLMENT_UPDATE_STATUS_PATH.format(id=request_id)
        return await self._client._patch(path, json=data.model_dump(mode="json", exclude_unset=True))

    # ---- Enrollment Request Timeline ----

    async def list_enrollment_timeline(
        self, params: EnrollmentTimelineParams | None = None, **kwargs: Any
    ) -> list[EnrollmentTimelineEntry]:
        """List enrollment request timeline entries (one page).

        Args:
            params: Optional query parameters (e.g. ``enrollment_request``, ``change_type``).
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            One page of timeline entries.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_ENROLLMENT_TIMELINE_PATH, params=raw_params)
        return [EnrollmentTimelineEntry.model_validate(i) for i in data.get("results", [])]

    async def list_enrollment_timeline_all(
        self, params: EnrollmentTimelineParams | None = None, **kwargs: Any
    ) -> list[EnrollmentTimelineEntry]:
        """List all enrollment request timeline entries (auto-paginates)."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ENROLLMENT_TIMELINE_PATH, params=raw_params)
        return [EnrollmentTimelineEntry.model_validate(i) for i in records]

    async def list_enrollment_timeline_df(
        self, params: EnrollmentTimelineParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        """Return all enrollment request timeline entries as a DataFrame."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ENROLLMENT_TIMELINE_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    # ---- OA Assignment ----

    async def list_reassignment_selectable_oa_users(
        self,
        enrollment_request: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        search: str | None = None,
    ) -> list[SelectableOaUser]:
        """List Operations Analyst users selectable for reassignment on an enrollment request.

        Args:
            enrollment_request: The enrollment request ID (required by the API).
            limit: Page size.
            offset: Page offset.
            search: Optional search term.

        Returns:
            One page of selectable OA users.
        """
        params: dict[str, Any] = {"enrollment_request": enrollment_request}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if search is not None:
            params["search"] = search
        data = await self._client._get_page(_SELECTABLE_OA_USERS_PATH, params=params)
        return [SelectableOaUser.model_validate(i) for i in data.get("results", [])]

    async def list_reassignment_selectable_oa_users_all(
        self, enrollment_request: str, *, search: str | None = None
    ) -> list[SelectableOaUser]:
        """List every Operations Analyst user selectable for reassignment (auto-paginates)."""
        params: dict[str, Any] = {"enrollment_request": enrollment_request}
        if search is not None:
            params["search"] = search
        records = await self._client._get_all_pages(_SELECTABLE_OA_USERS_PATH, params=params)
        return [SelectableOaUser.model_validate(i) for i in records]

    async def bulk_oa_assignment(self, data: BulkOaAssignment) -> dict[str, Any]:
        """Bulk-assign Operations Analysts to payer enrollment requests.

        Multiple OAs are distributed across matching requests in round-robin fashion.

        Args:
            data: The bulk assignment payload (``oas_to_assign`` and ``request_phase`` are
                required; target requests via ``enrollment_request_ids``, ``health_plan_ids``
                and/or ``states``).

        Returns:
            The raw response dict (``message`` and ``assigned_oas_data``).
        """
        return await self._client._post(_BULK_OA_ASSIGNMENT_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Active Enrollments ----

    async def list_active_enrollments(
        self, params: ActiveEnrollmentListParams | None = None, **kwargs: Any
    ) -> list[ActiveEnrollment]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_ACTIVE_ENROLLMENT_PATH, params=raw_params)
        return [ActiveEnrollment.model_validate(i) for i in data.get("results", [])]

    async def list_active_enrollments_all(
        self, params: ActiveEnrollmentListParams | None = None, **kwargs: Any
    ) -> list[ActiveEnrollment]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ACTIVE_ENROLLMENT_PATH, params=raw_params)
        return [ActiveEnrollment.model_validate(i) for i in records]

    async def list_active_enrollments_df(
        self, params: ActiveEnrollmentListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ACTIVE_ENROLLMENT_PATH, params=raw_params)
        return self._client.to_dataframe(records)
