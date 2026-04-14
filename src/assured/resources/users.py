"""Users resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.users import User, UserListParams

if TYPE_CHECKING:
    from assured.client import AssuredClient

_PATH = "/api/v1/users/users-list/"


class UsersResource:
    """Operations on user accounts."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def list(self, params: UserListParams | None = None, **kwargs: Any) -> list[User]:
        """Return a single page of users."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PATH, params=raw_params)
        return [User.model_validate(item) for item in data.get("results", [])]

    async def list_all(self, params: UserListParams | None = None, **kwargs: Any) -> list[User]:
        """Auto-paginate and return *all* users."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PATH, params=raw_params)
        return [User.model_validate(item) for item in records]

    async def list_df(self, params: UserListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        """Return all users as a DataFrame."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def login(self, email: str, password: str, remember: bool = True) -> str:
        """Programmatic login to acquire a short-lived session JWT.

        The Assured API natively relies on static long-lived API keys for integrations,
        but some undocumented and browser-specific endpoints (like the SSN update endpoint)
        strictly demand Bearer JWT authorization.

        This dynamically trades a user email and password for the active JWT access token.

        Returns:
            The raw JWT access string.
        """
        payload = {
            "email": email,
            "password": password,
            "remember": remember,
        }
        resp = await self._client._post("/api/v1/users/login/", json=payload)

        try:
            return resp["data"]["jwt"]["access"]
        except KeyError as e:
            from assured.exceptions import AssuredAPIError

            raise AssuredAPIError(
                500, f"Unexpected login response payload format: missing {e}", url="/api/v1/users/login/"
            ) from e

    async def password_reset(self, email: str) -> dict[str, Any]:
        """Trigger a password reset email for a given user or provider.

        Args:
            email: The email address to send the password reset link to.

        Returns:
            The raw JSON response from the server (typically empty on 200 OK).
        """
        return await self._client._post("/api/v1/users/password-reset/", json={"email": email})
