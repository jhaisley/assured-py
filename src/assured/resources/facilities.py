"""Facilities resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.facilities import FacilityListParams, FacilityProfile

if TYPE_CHECKING:
    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/facility/facility-profile-list/"


class FacilitiesResource:
    """Operations on facility profiles."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def list(self, params: FacilityListParams | None = None, **kwargs: Any) -> list[FacilityProfile]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [FacilityProfile.model_validate(i) for i in data.get("results", [])]

    async def list_all(self, params: FacilityListParams | None = None, **kwargs: Any) -> list[FacilityProfile]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [FacilityProfile.model_validate(i) for i in records]

    async def list_df(self, params: FacilityListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)
