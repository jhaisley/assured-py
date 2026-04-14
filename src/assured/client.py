"""Core async HTTP client for the Assured Platform API."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import httpx
import pandas as pd

from assured.exceptions import (
    AssuredAPIError,
    AssuredAuthError,
    AssuredNotFoundError,
    AssuredRateLimitError,
    AssuredValidationError,
)
from assured.settings import Settings

if TYPE_CHECKING:
    from assured.resources.account import AccountResource
    from assured.resources.credentialing import CredentialingResource
    from assured.resources.facilities import FacilitiesResource
    from assured.resources.files import FilesResource
    from assured.resources.hospital_affiliations import HospitalAffiliationsResource
    from assured.resources.payer_enrollment import PayerEnrollmentResource
    from assured.resources.practice_locations import PracticeLocationsResource
    from assured.resources.provider_profile import ProviderProfileResource
    from assured.resources.providers import ProvidersResource
    from assured.resources.tasks import TasksResource
    from assured.resources.tax_entities import TaxEntitiesResource
    from assured.resources.users import UsersResource

logger = logging.getLogger("assured")

_RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
_MAX_RETRIES = 3
_BACKOFF_BASE = 0.5  # seconds


class AssuredClient:
    """Async-first client for the Assured Platform API.

    Usage::

        async with AssuredClient() as client:
            users = await client.users.list()

    Or with explicit settings::

        settings = Settings(base_url="https://...", api_key="sk-...")
        async with AssuredClient(settings=settings) as client:
            ...
    """

    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._http: httpx.AsyncClient | None = None
        self._jwt_cache: str | None = None

        # Lazy-initialised resource helpers (cached on first access).
        self._users: UsersResource | None = None
        self._providers: ProvidersResource | None = None
        self._credentialing: CredentialingResource | None = None
        self._tasks: TasksResource | None = None
        self._provider_profile: ProviderProfileResource | None = None
        self._practice_locations: PracticeLocationsResource | None = None
        self._tax_entities: TaxEntitiesResource | None = None
        self._facilities: FacilitiesResource | None = None
        self._payer_enrollment: PayerEnrollmentResource | None = None
        self._hospital_affiliations: HospitalAffiliationsResource | None = None
        self._account: AccountResource | None = None
        self._files: FilesResource | None = None

    # ------------------------------------------------------------------
    # Context-manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AssuredClient:
        self._http = httpx.AsyncClient(
            base_url=self.settings.base_url.rstrip("/"),
            headers={"x-api-key": self.settings.api_key},
            timeout=httpx.Timeout(30.0),
        )
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None:
            msg = "Client not initialised — use `async with AssuredClient() as client:`"
            raise RuntimeError(msg)
        return self._http

    # ------------------------------------------------------------------
    # Resource properties
    # ------------------------------------------------------------------

    @property
    def users(self) -> UsersResource:
        if self._users is None:
            from assured.resources.users import UsersResource

            self._users = UsersResource(self)
        return self._users

    @property
    def providers(self) -> ProvidersResource:
        if self._providers is None:
            from assured.resources.providers import ProvidersResource

            self._providers = ProvidersResource(self)
        return self._providers

    @property
    def credentialing(self) -> CredentialingResource:
        if self._credentialing is None:
            from assured.resources.credentialing import CredentialingResource

            self._credentialing = CredentialingResource(self)
        return self._credentialing

    @property
    def tasks(self) -> TasksResource:
        if self._tasks is None:
            from assured.resources.tasks import TasksResource

            self._tasks = TasksResource(self)
        return self._tasks

    @property
    def provider_profile(self) -> ProviderProfileResource:
        if self._provider_profile is None:
            from assured.resources.provider_profile import ProviderProfileResource

            self._provider_profile = ProviderProfileResource(self)
        return self._provider_profile

    @property
    def practice_locations(self) -> PracticeLocationsResource:
        if self._practice_locations is None:
            from assured.resources.practice_locations import PracticeLocationsResource

            self._practice_locations = PracticeLocationsResource(self)
        return self._practice_locations

    @property
    def tax_entities(self) -> TaxEntitiesResource:
        if self._tax_entities is None:
            from assured.resources.tax_entities import TaxEntitiesResource

            self._tax_entities = TaxEntitiesResource(self)
        return self._tax_entities

    @property
    def facilities(self) -> FacilitiesResource:
        if self._facilities is None:
            from assured.resources.facilities import FacilitiesResource

            self._facilities = FacilitiesResource(self)
        return self._facilities

    @property
    def payer_enrollment(self) -> PayerEnrollmentResource:
        if self._payer_enrollment is None:
            from assured.resources.payer_enrollment import PayerEnrollmentResource

            self._payer_enrollment = PayerEnrollmentResource(self)
        return self._payer_enrollment

    @property
    def hospital_affiliations(self) -> HospitalAffiliationsResource:
        if self._hospital_affiliations is None:
            from assured.resources.hospital_affiliations import HospitalAffiliationsResource

            self._hospital_affiliations = HospitalAffiliationsResource(self)
        return self._hospital_affiliations

    @property
    def account(self) -> AccountResource:
        if self._account is None:
            from assured.resources.account import AccountResource

            self._account = AccountResource(self)
        return self._account

    @property
    def files(self) -> FilesResource:
        if self._files is None:
            from assured.resources.files import FilesResource

            self._files = FilesResource(self)
        return self._files

    # ------------------------------------------------------------------
    # Low-level HTTP helpers (with retry)
    # ------------------------------------------------------------------

    async def _get_jwt(self) -> str:
        """Fetch and cache a session JWT using credentials from settings."""
        if self._jwt_cache is None:
            if not self.settings.user or not self.settings.password:
                msg = "ASSURED_USER and ASSURED_PASS environment variables are required for JWT-based endpoints."
                raise RuntimeError(msg)
            self._jwt_cache = await self.users.login(self.settings.user, self.settings.password)
        return self._jwt_cache

    async def _request(self, method: str, path: str, *, requires_jwt: bool = False, **kwargs: Any) -> httpx.Response:
        """Execute an HTTP request with automatic retry & backoff."""
        if requires_jwt:
            jwt = await self._get_jwt()
            headers = kwargs.pop("headers", {}) or {}
            headers["Authorization"] = f"Bearer {jwt}"
            kwargs["headers"] = headers

        last_resp: httpx.Response | None = None
        for attempt in range(_MAX_RETRIES + 1):
            resp = await self.http.request(method, path, **kwargs)
            if resp.status_code not in _RETRY_STATUS_CODES or attempt == _MAX_RETRIES:
                last_resp = resp
                break
            wait = _BACKOFF_BASE * (2**attempt)
            logger.warning(
                "Retrying %s %s (status %d, attempt %d, wait %.1fs)", method, path, resp.status_code, attempt + 1, wait
            )
            await asyncio.sleep(wait)
            last_resp = resp

        assert last_resp is not None
        return last_resp

    def _raise_for_status(self, resp: httpx.Response) -> None:
        """Raise a typed exception for error status codes."""
        if resp.is_success:
            return
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text

        url = str(resp.url)
        match resp.status_code:
            case 400:
                raise AssuredValidationError(resp.status_code, detail, url=url)
            case 401:
                raise AssuredAuthError(resp.status_code, detail, url=url)
            case 404:
                raise AssuredNotFoundError(resp.status_code, detail, url=url)
            case 429:
                raise AssuredRateLimitError(resp.status_code, detail, url=url)
            case _:
                raise AssuredAPIError(resp.status_code, detail, url=url)

    async def _get(
        self, path: str, *, params: dict[str, Any] | None = None, requires_jwt: bool = False
    ) -> dict[str, Any]:
        resp = await self._request("GET", path, params=_clean_params(params), requires_jwt=requires_jwt)
        self._raise_for_status(resp)
        return resp.json()

    async def _post(
        self, path: str, *, json: Any = None, data: Any = None, files: Any = None, requires_jwt: bool = False
    ) -> dict[str, Any]:
        resp = await self._request("POST", path, json=json, data=data, files=files, requires_jwt=requires_jwt)
        self._raise_for_status(resp)
        return resp.json()

    async def _patch(self, path: str, *, json: Any = None, requires_jwt: bool = False) -> dict[str, Any]:
        resp = await self._request("PATCH", path, json=json, requires_jwt=requires_jwt)
        self._raise_for_status(resp)
        return resp.json()

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    async def _get_all_pages(self, path: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Fetch every page and return all ``results`` concatenated."""
        all_results: list[dict[str, Any]] = []
        params = dict(params or {})
        while True:
            data = await self._get(path, params=params)
            all_results.extend(data.get("results", []))
            next_url = data.get("next")
            if not next_url:
                break
            # The API returns absolute next URLs — extract offset/limit.
            parsed = httpx.URL(next_url)
            params["offset"] = parsed.params.get("offset", "0")
            if limit_val := parsed.params.get("limit"):
                params["limit"] = limit_val
        return all_results

    async def _get_page(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Fetch a single page and return the raw paginated response dict."""
        return await self._get(path, params=params)

    @staticmethod
    def to_dataframe(records: list[dict[str, Any]]) -> pd.DataFrame:
        """Convert a list of flat dicts to a pandas DataFrame."""
        return pd.json_normalize(records) if records else pd.DataFrame()


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Strip ``None`` values from query parameters."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
