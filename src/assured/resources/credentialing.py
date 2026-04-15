"""Credentialing resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.credentialing import (
    CredentialingListParams,
    CredentialingRequest,
    CredentialingRequestCreate,
    CredentialingRequestDetail,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_CREATE_PATH = "/api/v1/credentialing/create-credentialing-request/"
_DETAIL_PATH = "/api/v1/credentialing/request-detail/{id}/"
_LIST_PATH = "/api/v1/credentialing/request-list/"


class CredentialingResource:
    """Operations on credentialing requests."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def create_request(self, data: CredentialingRequestCreate) -> dict[str, Any]:
        """Create a new credentialing request."""
        return await self._client._post(_CREATE_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def get_request(self, request_id: str) -> CredentialingRequestDetail:
        """Get the detail/status of a credentialing request."""
        path = _DETAIL_PATH.format(id=request_id)
        data = await self._client._get(path)
        return CredentialingRequestDetail.model_validate(data)

    async def list_requests(
        self, params: CredentialingListParams | None = None, **kwargs: Any
    ) -> list[CredentialingRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [CredentialingRequest.model_validate(item) for item in data.get("results", [])]

    async def list_requests_all(
        self, params: CredentialingListParams | None = None, **kwargs: Any
    ) -> list[CredentialingRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [CredentialingRequest.model_validate(item) for item in records]

    async def list_requests_df(self, params: CredentialingListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)
