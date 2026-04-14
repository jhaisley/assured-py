"""Payer enrollment resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.payer_enrollment import (
    ActiveEnrollment,
    ActiveEnrollmentListParams,
    EnrollmentListParams,
    EnrollmentRequest,
    ExistingProviderEnrollment,
    ExistingProviderEnrollmentCreate,
    GroupEnrollmentRequestCreate,
    HealthPlan,
    ProviderEnrollmentRequestCreate,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_GROUP_ENROLL_PATH = "/api/v1/payer-enrollment/group-enrollment-request/"
_PROVIDER_ENROLL_PATH = "/api/v1/payer-enrollment/provider-enrollment-request/"
_HEALTH_PLAN_PATH = "/api/v1/payer-enrollment/health-plan/"
_ENROLLMENT_LIST_PATH = "/api/v1/payer-enrollment/enrollment-request-list/"
_ACTIVE_ENROLLMENT_PATH = "/api/v1/payer-enrollment/active-enrollment-list/"


class PayerEnrollmentResource:
    """Operations on payer enrollments."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    # ---- Create ----

    async def create_group_enrollment(self, data: GroupEnrollmentRequestCreate) -> dict[str, Any]:
        return await self._client._post(_GROUP_ENROLL_PATH, json=data.model_dump(exclude_none=False))

    async def create_provider_enrollment(self, data: ProviderEnrollmentRequestCreate) -> dict[str, Any]:
        return await self._client._post(_PROVIDER_ENROLL_PATH, json=data.model_dump(exclude_none=False))

    async def add_existing_provider_enrollment(self, data: ExistingProviderEnrollmentCreate) -> ExistingProviderEnrollment:
        path = "/api/v1/payer-enrollment/add-existing-provider-enrollment/"
        resp = await self._client._post(path, json=data.model_dump(exclude_none=False))
        return ExistingProviderEnrollment.model_validate(resp)

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
