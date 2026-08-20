"""Practice locations resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.practice_locations import (
    PracticeLocation,
    PracticeLocationCreate,
    PracticeLocationListParams,
    PracticeLocationProvider,
    PracticeLocationProviderListParams,
    ProviderPracticeLocationsBulkCreate,
)
from assured.models.providers import PracticeLocationProvidersCreate

if TYPE_CHECKING:
    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/clients/practice-locations/"
_DETAIL_PATH = "/api/v1/clients/practice-locations/{id}/"
_PROVIDER_LIST_PATH = "/api/v1/users/practice-location-provider/"
_PROVIDER_DETAIL_PATH = "/api/v1/users/practice-location-provider/{id}/"
_PROVIDER_CREATE_PATH = "/api/v1/users/practice-location-providers/"
_PROVIDER_BULK_PATH = "/api/v1/users/provider-practice-locations-bulk/"
_MARK_PRIMARY_PATH = "/api/v1/users/mark-primary-practice-location/{id}/"


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
        return await self._client._post(_LIST_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Practice location <-> provider associations ----

    async def list_providers(
        self,
        params: PracticeLocationProviderListParams | None = None,
        **kwargs: Any,
    ) -> list[PracticeLocationProvider]:
        """List practice-location/provider associations (one page).

        Args:
            params: Optional filter parameters (``provider``, ``practice_location``,
                ``practice_location__is_archived``, ``search``, ...).
            **kwargs: Extra query params merged over ``params``.

        Returns:
            One page of association records.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PROVIDER_LIST_PATH, params=raw_params)
        return [PracticeLocationProvider.model_validate(i) for i in data.get("results", [])]

    async def list_providers_all(
        self,
        params: PracticeLocationProviderListParams | None = None,
        **kwargs: Any,
    ) -> list[PracticeLocationProvider]:
        """List all practice-location/provider associations (auto-paginate).

        Args:
            params: Optional filter parameters.
            **kwargs: Extra query params merged over ``params``.

        Returns:
            All association records across every page.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PROVIDER_LIST_PATH, params=raw_params)
        return [PracticeLocationProvider.model_validate(i) for i in records]

    async def list_providers_df(
        self,
        params: PracticeLocationProviderListParams | None = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """List all practice-location/provider associations as a DataFrame.

        Args:
            params: Optional filter parameters.
            **kwargs: Extra query params merged over ``params``.

        Returns:
            A DataFrame with one row per association record.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PROVIDER_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_provider(self, association_id: str) -> PracticeLocationProvider:
        """Get a single practice-location/provider association by ID.

        Args:
            association_id: The association record ID.

        Returns:
            The association record.
        """
        path = _PROVIDER_DETAIL_PATH.format(id=association_id)
        data = await self._client._get(path)
        return PracticeLocationProvider.model_validate(data)

    async def delete_provider(self, association_id: str) -> dict[str, Any] | None:
        """Delete a practice-location/provider association.

        Args:
            association_id: The association record ID.

        Returns:
            The response body, or ``None`` when the API returns no content.
        """
        path = _PROVIDER_DETAIL_PATH.format(id=association_id)
        return await self._client._delete(path)

    async def create_provider(self, data: PracticeLocationProvidersCreate) -> dict[str, Any]:
        """Link one or more providers to a practice location.

        Hits the same endpoint as ``client.providers.add_to_practice_location``
        and shares its payload model; exposed here as well so the full
        association CRUD (list/get/create/delete/mark_primary) lives together.

        Args:
            data: The providers (IDs) and target practice location ID.

        Returns:
            The raw API response (``providers`` and ``practice_location``).
        """
        return await self._client._post(_PROVIDER_CREATE_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def create_provider_locations_bulk(self, data: ProviderPracticeLocationsBulkCreate) -> dict[str, Any]:
        """Bulk-link a provider to multiple practice locations.

        Args:
            data: The provider ID and practice location IDs to associate.

        Returns:
            The raw API response (``message``, ``created_count``, ``skipped_count``).
        """
        return await self._client._post(_PROVIDER_BULK_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def mark_primary(self, association_id: str, is_primary_location: bool = True) -> PracticeLocationProvider:
        """Mark a practice location as the provider's primary location.

        Args:
            association_id: The practice-location/provider association ID.
            is_primary_location: Whether the location should be primary (default ``True``).

        Returns:
            The updated association record.
        """
        path = _MARK_PRIMARY_PATH.format(id=association_id)
        data = await self._client._patch(path, json={"is_primary_location": is_primary_location})
        return PracticeLocationProvider.model_validate(data)
