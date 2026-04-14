"""Tests for the users resource."""

from __future__ import annotations

import httpx
import pytest
from tests.conftest import paginated_response

from assured.exceptions import AssuredAuthError, AssuredValidationError
from assured.models.users import UserListParams

_USERS_URL = "https://test-api.example.com/api/v1/users/users-list/"


@pytest.mark.asyncio
async def test_list_users(client, mock_api):
    """Happy-path: list returns parsed User objects."""
    mock_api.get(_USERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "abc-123",
                        "email": "alice@example.com",
                        "first_name": "Alice",
                        "last_name": "Smith",
                        "is_active": True,
                        "user_type": "provider",
                    },
                    {
                        "id": "def-456",
                        "email": "bob@example.com",
                        "first_name": "Bob",
                        "last_name": "Jones",
                        "is_active": False,
                        "user_type": "client_admin",
                    },
                ]
            ),
        )
    )

    users = await client.users.list()
    assert len(users) == 2
    assert users[0].email == "alice@example.com"
    assert users[1].is_active is False


@pytest.mark.asyncio
async def test_list_users_with_params(client, mock_api):
    """Ensure query params are forwarded."""
    route = mock_api.get(_USERS_URL).mock(return_value=httpx.Response(200, json=paginated_response([])))

    await client.users.list(UserListParams(is_active=True, search="alice"))
    assert route.called
    request = route.calls[0].request
    assert b"is_active" in request.url.query
    assert b"search" in request.url.query


@pytest.mark.asyncio
async def test_list_users_df(client, mock_api):
    """list_df returns a pandas DataFrame."""
    mock_api.get(_USERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "abc", "email": "a@b.com", "first_name": "A", "last_name": "B"},
                ]
            ),
        )
    )

    df = await client.users.list_df()
    assert len(df) == 1
    assert "email" in df.columns


@pytest.mark.asyncio
async def test_list_users_pagination(client, mock_api):
    """list_all follows next links."""
    mock_api.get(_USERS_URL).mock(
        side_effect=[
            httpx.Response(
                200,
                json=paginated_response(
                    [{"id": "1", "email": "a@b.com"}],
                    count=2,
                    next_url="https://test-api.example.com/api/v1/users/users-list/?offset=1&limit=1",
                ),
            ),
            httpx.Response(
                200,
                json=paginated_response([{"id": "2", "email": "c@d.com"}], count=2),
            ),
        ]
    )

    users = await client.users.list_all()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_list_users_401(client, mock_api):
    """401 raises AssuredAuthError."""
    mock_api.get(_USERS_URL).mock(return_value=httpx.Response(401, json={"detail": "Invalid API key"}))

    with pytest.raises(AssuredAuthError):
        await client.users.list()


@pytest.mark.asyncio
async def test_list_users_400(client, mock_api):
    """400 raises AssuredValidationError."""
    mock_api.get(_USERS_URL).mock(return_value=httpx.Response(400, json={"detail": "bad param"}))

    with pytest.raises(AssuredValidationError):
        await client.users.list()
