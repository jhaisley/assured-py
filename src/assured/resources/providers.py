"""Providers resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.providers import (
    CaqhImportRequest,
    CaqhImportRequestCreate,
    CaqhImportRequestListParams,
    PracticeLocationProvidersCreate,
    Provider,
    ProviderCAQHImport,
    ProviderCreate,
    ProviderInvite,
    ProviderListParams,
    ProviderOrgJoiningDate,
)

if TYPE_CHECKING:
    from datetime import date

    from assured.client import AssuredClient

_LIST_PATH = "/api/v1/users/providers-list/"
_INVITE_PATH = "/api/v1/users/invite-providers/"
_CAQH_PATH = "/api/v1/users/import-single-provider-with-caqh/"
_CREATE_PATH = "/api/v1/users/create-providers/"
_NOT_IN_PRACTICE_LOC_PATH = "/api/v1/users/providers-not-in-practice-loc/"
_PRACTICE_LOC_PROVIDERS_PATH = "/api/v1/users/practice-location-providers/"
_REQUEST_CAQH_IMPORT_PATH = "/api/v1/users/request-caqh-import/"
_ORG_JOINING_DATE_PATH = "/api/v1/users/update-provider-org-joining-date/{id}/"


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

    async def request_caqh_import(self, data: CaqhImportRequestCreate) -> dict[str, Any]:
        """Request a CAQH import (provider-authorized re-import).

        Args:
            data: The CAQH import request payload (``caqh_username``,
                ``caqh_password``, ``full_name`` and ``signature`` are all
                required by the spec).

        Returns:
            The created CAQH import request record as a raw dict.
        """
        return await self._client._post(
            _REQUEST_CAQH_IMPORT_PATH, json=data.model_dump(mode="json", exclude_none=False)
        )

    async def list_caqh_import_requests(
        self, params: CaqhImportRequestListParams | None = None, **kwargs: Any
    ) -> list[CaqhImportRequest]:
        """List CAQH import requests (one page).

        Args:
            params: Optional query parameters (``limit``, ``offset``,
                ``provider``).
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            The CAQH import request records for one page.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_REQUEST_CAQH_IMPORT_PATH, params=raw_params)
        return [CaqhImportRequest.model_validate(item) for item in data.get("results", [])]

    async def list_all_caqh_import_requests(
        self, params: CaqhImportRequestListParams | None = None, **kwargs: Any
    ) -> list[CaqhImportRequest]:
        """List all CAQH import requests (auto-paginated)."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_REQUEST_CAQH_IMPORT_PATH, params=raw_params)
        return [CaqhImportRequest.model_validate(item) for item in records]

    # ---- Create ----

    async def create(self, data: ProviderCreate) -> dict[str, Any]:
        """Create a new provider (without CAQH).

        The response dict matches
        :class:`~assured.models.providers.ProviderCreateResponse` (including
        ``source_of_joining``).
        """
        return await self._client._post(_CREATE_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Org Joining Date ----

    async def get_org_joining_date(self, provider_profile_id: str) -> ProviderOrgJoiningDate:
        """Retrieve a provider's organization joining date.

        Note:
            The path ``{id}`` for this endpoint is the provider **profile**
            ID (``provider_profile_id``), not the provider account ID — see
            ``API_Divergence.md`` section 4. Resolve it with
            :meth:`get_profile_id` if you only have the account ID.

        Args:
            provider_profile_id: The provider profile ID.

        Returns:
            The provider's organization joining date.
        """
        path = _ORG_JOINING_DATE_PATH.format(id=provider_profile_id)
        data = await self._client._get(path)
        return ProviderOrgJoiningDate.model_validate(data)

    async def update_org_joining_date(
        self, provider_profile_id: str, org_joining_date: date | str | None
    ) -> ProviderOrgJoiningDate:
        """Update a provider's organization joining date.

        Note:
            The path ``{id}`` for this endpoint is the provider **profile**
            ID (``provider_profile_id``), not the provider account ID — see
            ``API_Divergence.md`` section 4. Resolve it with
            :meth:`get_profile_id` if you only have the account ID.

        Args:
            provider_profile_id: The provider profile ID.
            org_joining_date: The new joining date (``datetime.date`` or
                ``YYYY-MM-DD`` string).

        Returns:
            The updated provider organization joining date record.
        """
        value = org_joining_date.isoformat() if hasattr(org_joining_date, "isoformat") else org_joining_date
        path = _ORG_JOINING_DATE_PATH.format(id=provider_profile_id)
        data = await self._client._patch(path, json={"org_joining_date": value})
        return ProviderOrgJoiningDate.model_validate(data)

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
