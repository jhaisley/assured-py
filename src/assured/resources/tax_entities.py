"""Tax entities resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.tax_entities import TaxEntity, TaxEntityCreate, TaxEntityListParams

if TYPE_CHECKING:
    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/clients/tax-entities/"
_DETAIL_PATH = "/api/v1/clients/tax-entities/{id}/"


class TaxEntitiesResource:
    """Operations on tax entities."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def list(self, params: TaxEntityListParams | None = None, **kwargs: Any) -> list[TaxEntity]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [TaxEntity.model_validate(i) for i in data.get("results", [])]

    async def list_all(self, params: TaxEntityListParams | None = None, **kwargs: Any) -> list[TaxEntity]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [TaxEntity.model_validate(i) for i in records]

    async def list_df(self, params: TaxEntityListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get(self, entity_id: str) -> TaxEntity:
        path = _DETAIL_PATH.format(id=entity_id)
        data = await self._client._get(path)
        return TaxEntity.model_validate(data)

    async def create(self, data: TaxEntityCreate) -> dict[str, Any]:
        return await self._client._post(_LIST_PATH, json=data.model_dump(mode="json", exclude_none=False))
