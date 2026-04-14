"""Account resource (password management)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from assured.client import AssuredClient

_CHANGE_PASSWORD_PATH = "/api/v1/users/change-password/"


class AccountResource:
    """Account management operations."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def change_password(self, *, old_password: str, new_password: str) -> dict[str, Any]:
        """Change the authenticated user's password."""
        return await self._client._post(
            _CHANGE_PASSWORD_PATH,
            json={"old_password": old_password, "new_password": new_password},
        )
