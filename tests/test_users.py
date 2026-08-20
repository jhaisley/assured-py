"""Tests for the users resource."""

from __future__ import annotations

import httpx
import pytest

from assured.exceptions import AssuredAPIError, AssuredAuthError, AssuredValidationError
from assured.models.users import UserListParams, UserSlimListParams
from tests.conftest import paginated_response

_USERS_URL = "https://test-api.example.com/api/v1/users/external-users-list/"
_SLIM_URL = "https://test-api.example.com/api/v1/users/user-list-slim/"
_LOGGED_IN_URL = "https://test-api.example.com/api/v1/users/logged-in-user-details/"
_LOGIN_URL = "https://test-api.example.com/api/v1/users/login/"


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
                    next_url="https://test-api.example.com/api/v1/users/external-users-list/?offset=1&limit=1",
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


@pytest.mark.asyncio
async def test_list_slim(client, mock_api):
    """list_slim returns parsed UserSlim objects."""
    mock_api.get(_SLIM_URL).mock(
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

    users = await client.users.list_slim()
    assert len(users) == 2
    assert users[0].email == "alice@example.com"
    assert users[0].user_type == "provider"
    assert users[1].is_active is False


@pytest.mark.asyncio
async def test_list_slim_with_params(client, mock_api):
    """Ensure slim-list query params are forwarded."""
    route = mock_api.get(_SLIM_URL).mock(return_value=httpx.Response(200, json=paginated_response([])))

    await client.users.list_slim(UserSlimListParams(user_type="provider", include_unverified=True, search="alice"))
    assert route.called
    request = route.calls[0].request
    assert b"user_type" in request.url.query
    assert b"include_unverified" in request.url.query
    assert b"search" in request.url.query


@pytest.mark.asyncio
async def test_list_slim_all_pagination(client, mock_api):
    """list_slim_all follows next links."""
    mock_api.get(_SLIM_URL).mock(
        side_effect=[
            httpx.Response(
                200,
                json=paginated_response(
                    [{"id": "1", "email": "a@b.com"}],
                    count=2,
                    next_url="https://test-api.example.com/api/v1/users/user-list-slim/?offset=1&limit=1",
                ),
            ),
            httpx.Response(
                200,
                json=paginated_response([{"id": "2", "email": "c@d.com"}], count=2),
            ),
        ]
    )

    users = await client.users.list_slim_all()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_list_slim_df(client, mock_api):
    """list_slim_df returns a pandas DataFrame."""
    mock_api.get(_SLIM_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "abc", "email": "a@b.com", "first_name": "A", "last_name": "B"},
                ]
            ),
        )
    )

    df = await client.users.list_slim_df()
    assert len(df) == 1
    assert "email" in df.columns


@pytest.mark.asyncio
async def test_get_logged_in_user(client, mock_api):
    """get_logged_in_user returns a parsed LoggedInUserDetails."""
    mock_api.get(_LOGGED_IN_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "abc-123",
                "email": "alice@example.com",
                "first_name": "Alice",
                "middle_name": "Q",
                "last_name": "Smith",
                "user_type": "client_admin",
                "is_active": True,
                "provider_profile": None,
                "extra_data": {"client_exists": True, "mfa_config": {"enabled": False}},
                "provider_profile_completion_info": {"completion_percent": 80.0},
                "user_associated_features": ["licensing", "payor_enrollment"],
                "credentialing_readiness_info": None,
                "assured_user_id": "au-1",
            },
        )
    )

    me = await client.users.get_logged_in_user()
    assert me.email == "alice@example.com"
    assert me.user_type == "client_admin"
    assert me.extra_data["client_exists"] is True
    assert me.user_associated_features == ["licensing", "payor_enrollment"]
    assert me.assured_user_id == "au-1"


@pytest.mark.asyncio
async def test_login_returns_access_token(client, mock_api):
    """login extracts the JWT access string from the documented response."""
    mock_api.post(_LOGIN_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "abc-123",
                    "email": "alice@example.com",
                    "user_type": "client_admin",
                    "is_active": True,
                    "jwt": {"refresh": "refresh-token", "access": "access-token"},
                },
                "msg": "Login successful",
                "extra_data": {"client_exists": True},
            },
        )
    )

    token = await client.users.login("alice@example.com", "secret")
    assert token == "access-token"


@pytest.mark.asyncio
async def test_login_unexpected_payload(client, mock_api):
    """login raises AssuredAPIError when the JWT is missing from the response."""
    mock_api.post(_LOGIN_URL).mock(return_value=httpx.Response(200, json={"data": {}}))

    with pytest.raises(AssuredAPIError):
        await client.users.login("alice@example.com", "secret")


@pytest.mark.asyncio
async def test_login_full(client, mock_api):
    """login_full returns the entire documented response payload."""
    payload = {
        "data": {
            "id": "abc-123",
            "email": "alice@example.com",
            "jwt": {"refresh": "refresh-token", "access": "access-token"},
        },
        "msg": "Login successful",
        "extra_data": {"client_exists": True, "user_associated_features": ["licensing"]},
    }
    mock_api.post(_LOGIN_URL).mock(return_value=httpx.Response(200, json=payload))

    resp = await client.users.login_full("alice@example.com", "secret")
    assert resp["data"]["jwt"]["refresh"] == "refresh-token"
    assert resp["msg"] == "Login successful"
    assert resp["extra_data"]["client_exists"] is True
