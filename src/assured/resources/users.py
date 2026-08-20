"""Users resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.users import LoggedInUserDetails, User, UserListParams, UserSlim, UserSlimListParams

if TYPE_CHECKING:
    from assured.client import AssuredClient

_PATH = "/api/v1/users/external-users-list/"
_SLIM_PATH = "/api/v1/users/user-list-slim/"
_LOGGED_IN_USER_PATH = "/api/v1/users/logged-in-user-details/"
_LOGIN_PATH = "/api/v1/users/login/"


class UsersResource:
    """Operations on user accounts."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def list(self, params: UserListParams | None = None, **kwargs: Any) -> list[User]:
        """Return a single page of users.

        Note:
            This uses the undocumented ``external-users-list`` endpoint. The formerly
            documented ``/api/v1/users/users-list/`` endpoint has been removed from the
            API spec entirely; ``external-users-list`` continues to work. For the
            officially documented slim listing, see :meth:`list_slim`.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PATH, params=raw_params)
        return [User.model_validate(item) for item in data.get("results", [])]

    async def list_all(self, params: UserListParams | None = None, **kwargs: Any) -> list[User]:
        """Auto-paginate and return *all* users.

        Note:
            Uses the undocumented ``external-users-list`` endpoint (the documented
            ``users-list`` endpoint no longer exists). See :meth:`list`.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PATH, params=raw_params)
        return [User.model_validate(item) for item in records]

    async def list_df(self, params: UserListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        """Return all users as a DataFrame.

        Note:
            Uses the undocumented ``external-users-list`` endpoint (the documented
            ``users-list`` endpoint no longer exists). See :meth:`list`.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def list_slim(self, params: UserSlimListParams | None = None, **kwargs: Any) -> list[UserSlim]:
        """Return a single page of slim user records.

        Wraps the documented ``GET /api/v1/users/user-list-slim/`` endpoint, which
        returns a reduced user payload (id, email, name, active flag, user type).

        Args:
            params: Optional typed query parameters.
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            One page of :class:`~assured.models.users.UserSlim` records.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_SLIM_PATH, params=raw_params)
        return [UserSlim.model_validate(item) for item in data.get("results", [])]

    async def list_slim_all(self, params: UserSlimListParams | None = None, **kwargs: Any) -> list[UserSlim]:
        """Auto-paginate and return *all* slim user records.

        Args:
            params: Optional typed query parameters.
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            All :class:`~assured.models.users.UserSlim` records across pages.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_SLIM_PATH, params=raw_params)
        return [UserSlim.model_validate(item) for item in records]

    async def list_slim_df(self, params: UserSlimListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        """Return all slim user records as a DataFrame.

        Args:
            params: Optional typed query parameters.
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            A pandas DataFrame with one row per user.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_SLIM_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_logged_in_user(self, *, requires_jwt: bool = False) -> LoggedInUserDetails:
        """Return details of the currently authenticated user.

        Wraps the documented ``GET /api/v1/users/logged-in-user-details/`` endpoint.

        Args:
            requires_jwt: Send a Bearer JWT (acquired via :meth:`login` credentials)
                instead of relying solely on the API key, mirroring how the browser
                app calls this endpoint.

        Returns:
            A :class:`~assured.models.users.LoggedInUserDetails` instance. Nested
            profile/feature structures are kept as permissive dicts.
        """
        data = await self._client._get(_LOGGED_IN_USER_PATH, requires_jwt=requires_jwt)
        return LoggedInUserDetails.model_validate(data)

    async def login(self, email: str, password: str, remember: bool = True) -> str:
        """Programmatic login to acquire a short-lived session JWT.

        Wraps the officially documented ``POST /api/v1/users/login/`` endpoint
        (operationId ``userLogin``). The Assured API natively relies on static
        long-lived API keys for integrations, but some browser-oriented endpoints
        (like the SSN update endpoint) strictly demand Bearer JWT authorization.

        This trades a user email and password for the active JWT access token. The
        documented response also carries a refresh token (``data.jwt.refresh``),
        basic user info (``data.id`` / ``email`` / ``user_type`` / ``is_active``),
        a ``msg`` string, and an ``extra_data`` object (client details, MFA config,
        enabled feature flags); use :meth:`login_full` if you need those.

        Note:
            The ``remember`` flag is accepted by the server but not part of the
            documented request schema (which lists only ``email`` and ``password``).

        Returns:
            The raw JWT access string.
        """
        payload = {
            "email": email,
            "password": password,
            "remember": remember,
        }
        resp = await self._client._post(_LOGIN_PATH, json=payload)

        try:
            return resp["data"]["jwt"]["access"]
        except KeyError as e:
            from assured.exceptions import AssuredAPIError

            raise AssuredAPIError(500, f"Unexpected login response payload format: missing {e}", url=_LOGIN_PATH) from e

    async def login_full(self, email: str, password: str, remember: bool = True) -> dict[str, Any]:
        """Login and return the full documented response payload.

        Unlike :meth:`login`, which extracts only the JWT access token, this returns
        the entire response documented for ``POST /api/v1/users/login/``:

        - ``data``: user info (``id``, ``email``, ``first_name``, ``last_name``,
          ``user_type``, ``is_active``) plus ``jwt.access`` / ``jwt.refresh``.
        - ``msg``: human-readable status message.
        - ``extra_data``: account context — ``client_exists``, ``client_details``,
          ``tax_entity_exists``, ``provider_profile_id``, ``min_profile_completed``,
          ``caqh_account_exists``, ``user_associated_features``, MFA config, etc.

        Returns:
            The raw JSON response as a dict.
        """
        payload = {
            "email": email,
            "password": password,
            "remember": remember,
        }
        return await self._client._post(_LOGIN_PATH, json=payload)

    async def password_reset(self, email: str) -> dict[str, Any]:
        """Trigger a password reset email for a given user or provider.

        Args:
            email: The email address to send the password reset link to.

        Returns:
            The raw JSON response from the server (typically empty on 200 OK).
        """
        return await self._client._post("/api/v1/users/password-reset/", json={"email": email})
