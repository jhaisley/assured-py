"""Tests for the providers resource."""

from __future__ import annotations

import httpx
import pytest

from assured.models.providers import ProviderCreate, ProviderInvite
from tests.conftest import paginated_response

_PROVIDERS_URL = "https://test-api.example.com/api/v1/users/providers-list/"
_INVITE_URL = "https://test-api.example.com/api/v1/users/invite-providers/"
_CREATE_URL = "https://test-api.example.com/api/v1/users/create-providers/"


@pytest.mark.asyncio
async def test_list_providers(client, mock_api):
    mock_api.get(_PROVIDERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "p-1",
                        "email": "doc@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "npi": "1234567890",
                        "profile_completeness_percentage": 85.0,
                    },
                ]
            ),
        )
    )

    providers = await client.providers.list()
    assert len(providers) == 1
    assert providers[0].npi == "1234567890"


@pytest.mark.asyncio
async def test_list_providers_df(client, mock_api):
    mock_api.get(_PROVIDERS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "p-1", "email": "doc@example.com", "first_name": "Jane", "last_name": "Doe"},
                ]
            ),
        )
    )

    df = await client.providers.list_df()
    assert "first_name" in df.columns


@pytest.mark.asyncio
async def test_invite_providers(client, mock_api):
    mock_api.post(_INVITE_URL).mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "new-1", "email": "new@example.com", "first_name": "New", "last_name": "Doc"}],
        )
    )

    result = await client.providers.invite(
        [
            ProviderInvite(email="new@example.com", first_name="New", last_name="Doc"),
        ]
    )
    assert result[0]["id"] == "new-1"


@pytest.mark.asyncio
async def test_create_provider(client, mock_api):
    mock_api.post(_CREATE_URL).mock(
        return_value=httpx.Response(
            201,
            json={"id": "created-1", "email": "created@example.com", "first_name": "C", "last_name": "D"},
        )
    )

    result = await client.providers.create(ProviderCreate(email="created@example.com", first_name="C", last_name="D"))
    assert result["id"] == "created-1"


@pytest.mark.asyncio
async def test_get_provider_success(client, mock_api):
    # Setting up the mock list endpoint to filter by id_in
    mock_api.get(f"{_PROVIDERS_URL}?id_in=p-1").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "p-1",
                        "email": "doc@example.com",
                        "first_name": "Jane",
                        "provider_profile_id": "prof-1",
                    },
                ]
            ),
        )
    )

    provider = await client.providers.get("p-1")
    assert provider.id == "p-1"
    assert provider.provider_profile_id == "prof-1"


@pytest.mark.asyncio
async def test_get_provider_not_found(client, mock_api):
    from assured.exceptions import AssuredNotFoundError

    mock_api.get(f"{_PROVIDERS_URL}?id_in=p-missing").mock(
        return_value=httpx.Response(200, json=paginated_response([]))
    )

    with pytest.raises(AssuredNotFoundError, match="No provider found with id=p-missing"):
        await client.providers.get("p-missing")


@pytest.mark.asyncio
async def test_get_profile_id_success(client, mock_api):
    mock_api.get(f"{_PROVIDERS_URL}?id_in=p-1").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "p-1",
                        "provider_profile_id": "prof-123",
                    },
                ]
            ),
        )
    )

    profile_id = await client.providers.get_profile_id("p-1")
    assert profile_id == "prof-123"


@pytest.mark.asyncio
async def test_get_profile_id_missing(client, mock_api):
    from assured.exceptions import AssuredAPIError

    mock_api.get(f"{_PROVIDERS_URL}?id_in=p-no-prof").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "p-no-prof",
                        "provider_profile_id": None,  # No profile id
                    },
                ]
            ),
        )
    )

    with pytest.raises(AssuredAPIError, match="Provider p-no-prof has no profile ID"):
        await client.providers.get_profile_id("p-no-prof")
