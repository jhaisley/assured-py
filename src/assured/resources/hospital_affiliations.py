"""Hospital affiliations resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.hospital_affiliations import (
    AdmittingArrangement,
    AdmittingArrangementCreate,
    AdmittingPrivilege,
    AdmittingPrivilegeCreate,
    HospitalAffiliationListParams,
    NonAdmittingAffiliation,
    NonAdmittingAffiliationCreate,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_ARRANGEMENTS_PATH = "/api/v1/users/provider-hospital-with-admitting-arrangements/"
_ARRANGEMENTS_DETAIL = "/api/v1/users/provider-hospital-with-admitting-arrangements/{id}/"
_PRIVILEGES_PATH = "/api/v1/users/provider-hospital-with-admitting-privileges/"
_PRIVILEGES_DETAIL = "/api/v1/users/provider-hospital-with-admitting-privileges/{id}/"
_NON_ADMITTING_PATH = "/api/v1/users/provider-hospital-with-non-admitting-affiliations/"
_NON_ADMITTING_DETAIL = "/api/v1/users/provider-hospital-with-non-admitting-affiliations/{id}/"


class HospitalAffiliationsResource:
    """Operations on hospital affiliations."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    # ---- Admitting Arrangements ----

    async def list_arrangements(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[AdmittingArrangement]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_ARRANGEMENTS_PATH, params=raw_params)
        return [AdmittingArrangement.model_validate(i) for i in data.get("results", [])]

    async def list_arrangements_all(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[AdmittingArrangement]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ARRANGEMENTS_PATH, params=raw_params)
        return [AdmittingArrangement.model_validate(i) for i in records]

    async def list_arrangements_df(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_ARRANGEMENTS_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_arrangement(self, arrangement_id: str) -> AdmittingArrangement:
        data = await self._client._get(_ARRANGEMENTS_DETAIL.format(id=arrangement_id))
        return AdmittingArrangement.model_validate(data)

    async def create_arrangement(self, data: AdmittingArrangementCreate) -> dict[str, Any]:
        return await self._client._post(_ARRANGEMENTS_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Admitting Privileges ----

    async def list_privileges(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[AdmittingPrivilege]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PRIVILEGES_PATH, params=raw_params)
        return [AdmittingPrivilege.model_validate(i) for i in data.get("results", [])]

    async def list_privileges_all(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[AdmittingPrivilege]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PRIVILEGES_PATH, params=raw_params)
        return [AdmittingPrivilege.model_validate(i) for i in records]

    async def list_privileges_df(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PRIVILEGES_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_privilege(self, privilege_id: str) -> AdmittingPrivilege:
        data = await self._client._get(_PRIVILEGES_DETAIL.format(id=privilege_id))
        return AdmittingPrivilege.model_validate(data)

    async def create_privilege(self, data: AdmittingPrivilegeCreate) -> dict[str, Any]:
        return await self._client._post(_PRIVILEGES_PATH, json=data.model_dump(mode="json", exclude_none=False))

    # ---- Non-Admitting Affiliations ----

    async def list_non_admitting(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[NonAdmittingAffiliation]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_NON_ADMITTING_PATH, params=raw_params)
        return [NonAdmittingAffiliation.model_validate(i) for i in data.get("results", [])]

    async def list_non_admitting_all(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> list[NonAdmittingAffiliation]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_NON_ADMITTING_PATH, params=raw_params)
        return [NonAdmittingAffiliation.model_validate(i) for i in records]

    async def list_non_admitting_df(
        self, params: HospitalAffiliationListParams | None = None, **kwargs: Any
    ) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_NON_ADMITTING_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_non_admitting(self, affiliation_id: str) -> NonAdmittingAffiliation:
        data = await self._client._get(_NON_ADMITTING_DETAIL.format(id=affiliation_id))
        return NonAdmittingAffiliation.model_validate(data)

    async def create_non_admitting(self, data: NonAdmittingAffiliationCreate) -> dict[str, Any]:
        return await self._client._post(_NON_ADMITTING_PATH, json=data.model_dump(mode="json", exclude_none=False))
