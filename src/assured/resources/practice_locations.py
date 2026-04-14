"""Practice locations resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.practice_locations import (
    PracticeLocation,
    PracticeLocationCreate,
    PracticeLocationListParams,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/clients/practice-locations/"
_DETAIL_PATH = "/api/v1/clients/practice-locations/{id}/"


class PracticeLocationsResource:
    """Operations on practice locations."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def list(self, params: PracticeLocationListParams | None = None, **kwargs: Any) -> list[PracticeLocation]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [PracticeLocation.model_validate(i) for i in data.get("results", [])]

    async def list_all(self, params: PracticeLocationListParams | None = None, **kwargs: Any) -> list[PracticeLocation]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [PracticeLocation.model_validate(i) for i in records]

    async def list_df(self, params: PracticeLocationListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get(self, location_id: str) -> PracticeLocation:
        path = _DETAIL_PATH.format(id=location_id)
        data = await self._client._get(path)
        return PracticeLocation.model_validate(data)

    async def create(self, data: PracticeLocationCreate) -> dict[str, Any]:
        return await self._client._post(_LIST_PATH, json=data.model_dump(exclude_none=False))
