"""Providers resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.providers import (
    PracticeLocationProvidersCreate,
    Provider,
    ProviderCAQHImport,
    ProviderCreate,
    ProviderInvite,
    ProviderListParams,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/users/providers-list/"
_INVITE_PATH = "/api/v1/users/invite-providers/"
_CAQH_PATH = "/api/v1/users/import-single-provider-with-caqh/"
_CREATE_PATH = "/api/v1/users/create-providers/"
_NOT_IN_PRACTICE_LOC_PATH = "/api/v1/users/providers-not-in-practice-loc/"
_PRACTICE_LOC_PROVIDERS_PATH = "/api/v1/users/practice-location-providers/"


class ProvidersResource:
    """Operations on provider accounts."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client
        self._npi_cache: dict[str, Provider] = {}
        self._npi_cache_time: float = 0.0

    # ---- List ----

    async def list(self, params: ProviderListParams | None = None, **kwargs: Any) -> list[Provider]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [Provider.model_validate(item) for item in data.get("results", [])]

    async def list_all(self, params: ProviderListParams | None = None, **kwargs: Any) -> list[Provider]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [Provider.model_validate(item) for item in records]

    async def list_df(self, params: ProviderListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    # ---- Get ----

    async def get(self, provider_id: str) -> Provider:
        """Fetch a single provider by account ID.

        Uses the list endpoint filtered by ``id_in`` and returns the
        first (and only) match.
        """
        results = await self.list(ProviderListParams(id_in=provider_id))
        if not results:
            from assured.exceptions import AssuredNotFoundError

            raise AssuredNotFoundError(
                404,
                f"No provider found with id={provider_id}",
                url=_LIST_PATH,
            )
        return results[0]

    async def get_profile_id(self, provider_id: str) -> str:
        """Resolve a provider account ID → provider_profile_id.

        Many profile endpoints (personal-info, certifications, licenses,
        insurance, etc.) require the ``provider_profile_id`` rather than
        the account ``id``.  This helper performs the lookup.
        """
        provider = await self.get(provider_id)
        if not provider.provider_profile_id:
            from assured.exceptions import AssuredAPIError

            raise AssuredAPIError(
                422,
                f"Provider {provider_id} has no profile ID",
                url=_LIST_PATH,
            )
        return provider.provider_profile_id

    async def get_by_npi(self, npi: str) -> Provider:
        """Fetch a single provider by their NPI.

        Since there is no native endpoint for NPI lookup, this pulls the
        full provider list and caches it for 5 minutes to optimize
        subsequent identical calls.
        """
        import time

        # Cache validity for 300 seconds (5 minutes)
        if time.time() - self._npi_cache_time > 300:
            all_providers = await self.list_all()
            self._npi_cache = {p.npi: p for p in all_providers if getattr(p, "npi", None)}
            self._npi_cache_time = time.time()

        provider = self._npi_cache.get(npi)
        if not provider:
            from assured.exceptions import AssuredNotFoundError

            raise AssuredNotFoundError(
                404,
                f"No provider found across the company with NPI={npi}",
                url=_LIST_PATH,
            )
        return provider

    # ---- Invite ----

    async def invite(self, providers: list[ProviderInvite]) -> list[dict[str, Any]]:
        """Invite one or more providers to the platform."""
        payload = [p.model_dump(mode="json", exclude_none=False) for p in providers]
        return await self._client._post(_INVITE_PATH, json=payload)

    # ---- CAQH Import ----

    async def import_with_caqh(self, data: ProviderCAQHImport) -> dict[str, Any]:
        """Import a single provider using CAQH credentials."""
        return await self._client._post(_CAQH_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Create ----

    async def create(self, data: ProviderCreate) -> dict[str, Any]:
        """Create a new provider (without CAQH)."""
        return await self._client._post(_CREATE_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Practice Locations ----

    async def list_not_in_practice_location(
        self, practice_location: str, params: ProviderListParams | None = None, **kwargs: Any
    ) -> list[Provider]:
        """List providers not associated with a specific practice location."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        raw_params["practice_location"] = practice_location
        data = await self._client._get_page(_NOT_IN_PRACTICE_LOC_PATH, params=raw_params)
        return [Provider.model_validate(item) for item in data.get("results", [])]

    async def list_all_not_in_practice_location(
        self, practice_location: str, params: ProviderListParams | None = None, **kwargs: Any
    ) -> list[Provider]:
        """List all providers not associated with a specific practice location."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        raw_params["practice_location"] = practice_location
        records = await self._client._get_all_pages(_NOT_IN_PRACTICE_LOC_PATH, params=raw_params)
        return [Provider.model_validate(item) for item in records]

    async def list_not_in_practice_location_df(
        self, practice_location: str, params: ProviderListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        """List all providers not associated with a specific practice location as a DataFrame."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        raw_params["practice_location"] = practice_location
        records = await self._client._get_all_pages(_NOT_IN_PRACTICE_LOC_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def add_to_practice_location(self, data: PracticeLocationProvidersCreate) -> dict[str, Any]:
        """Associate multiple providers with a practice location."""
        return await self._client._post(
            _PRACTICE_LOC_PROVIDERS_PATH, json=data.model_dump(mode="json", exclude_none=False)
        )
