"""Tests for the providers resource."""

from __future__ import annotations

import httpx
import pytest

from assured.models.providers import (
    CaqhImportRequestCreate,
    CaqhImportRequestListParams,
    PracticeLocationProvidersCreate,
    ProviderCAQHImport,
    ProviderCreate,
    ProviderInvite,
    ProviderListParams,
)
from tests.conftest import paginated_response

_PROVIDERS_URL = "https://test-api.example.com/api/v1/users/providers-list/"
_INVITE_URL = "https://test-api.example.com/api/v1/users/invite-providers/"
_CREATE_URL = "https://test-api.example.com/api/v1/users/create-providers/"
_CAQH_IMPORT_URL = "https://test-api.example.com/api/v1/users/import-single-provider-with-caqh/"
_REQUEST_CAQH_IMPORT_URL = "https://test-api.example.com/api/v1/users/request-caqh-import/"
_ORG_JOINING_DATE_URL = "https://test-api.example.com/api/v1/users/update-provider-org-joining-date/prof-1/"
_NOT_IN_PRACTICE_LOC_URL = "https://test-api.example.com/api/v1/users/providers-not-in-practice-loc/"
_PRACTICE_LOC_PROVIDERS_URL = "https://test-api.example.com/api/v1/users/practice-location-providers/"


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

    result = await client.providers.create(
        ProviderCreate(
            email="created@example.com",
            first_name="C",
            last_name="D",
            client="client-id",
            document_url="https://example.com/doc.pdf",
            document_type="W-9",
        )
    )
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


@pytest.mark.asyncio
async def test_list_not_in_practice_location(client, mock_api):
    mock_api.get(f"{_NOT_IN_PRACTICE_LOC_URL}?practice_location=loc-1").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "p-1",
                        "email": "doc@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "is_active": True,
                        "user_type": "provider",
                    },
                ]
            ),
        )
    )

    providers = await client.providers.list_not_in_practice_location(practice_location="loc-1")
    assert len(providers) == 1
    assert providers[0].id == "p-1"
    assert providers[0].is_active is True
    assert providers[0].user_type == "provider"


@pytest.mark.asyncio
async def test_list_providers_new_filters(client, mock_api):
    route = mock_api.get(f"{_PROVIDERS_URL}?client=client-1&client_in=client-1,client-2&is_active=true").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "p-1", "email": "doc@example.com", "is_active": True},
                ]
            ),
        )
    )

    providers = await client.providers.list(
        ProviderListParams(client="client-1", client_in="client-1,client-2", is_active=True)
    )
    assert route.called
    assert len(providers) == 1
    assert providers[0].is_active is True


@pytest.mark.asyncio
async def test_create_provider_minimal_with_primary_location(client, mock_api):
    route = mock_api.post(_CREATE_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "created-2",
                "email": "min@example.com",
                "first_name": "Min",
                "last_name": "Imal",
                "primary_practice_location": None,
                "source_of_joining": "PROVIDER_CREATE_API",
            },
        )
    )

    result = await client.providers.create(
        ProviderCreate(
            email="min@example.com",
            first_name="Min",
            last_name="Imal",
            primary_practice_location="loc-1",
        )
    )
    assert result["source_of_joining"] == "PROVIDER_CREATE_API"

    import json

    sent = json.loads(route.calls.last.request.content)
    assert sent["primary_practice_location"] == "loc-1"
    # Unset optional fields must be omitted, not sent as null: the spec types
    # client / document_url / document_type as non-nullable strings, and
    # production answers an explicit null with HTTP 400 "This field may not be
    # null." even though all three are optional.
    for omitted in ("client", "document_url", "document_type", "org_joining_date"):
        assert omitted not in sent


@pytest.mark.asyncio
async def test_import_with_caqh(client, mock_api):
    mock_api.post(_CAQH_IMPORT_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "imp-1",
                "email": "caqh@example.com",
                "primary_practice_location": None,
            },
        )
    )

    result = await client.providers.import_with_caqh(
        ProviderCAQHImport(
            email="caqh@example.com",
            caqh_username="caqh_user",
            caqh_password="caqh_pass",
            primary_practice_location="loc-1",
        )
    )
    assert result["id"] == "imp-1"


@pytest.mark.asyncio
async def test_request_caqh_import(client, mock_api):
    mock_api.post(_REQUEST_CAQH_IMPORT_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 7,
                "caqh_username": "caqh_user",
                "caqh_password": "caqh_pass",
                "full_name": "Jane Doe",
                "signature": "Jane Doe",
            },
        )
    )

    result = await client.providers.request_caqh_import(
        CaqhImportRequestCreate(
            caqh_username="caqh_user",
            caqh_password="caqh_pass",
            full_name="Jane Doe",
            signature="Jane Doe",
        )
    )
    assert result["id"] == 7


@pytest.mark.asyncio
async def test_list_caqh_import_requests(client, mock_api):
    mock_api.get(f"{_REQUEST_CAQH_IMPORT_URL}?provider=p-1").mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": 1, "caqh_username": "u1", "full_name": "Jane Doe", "signature": "Jane Doe"},
                ]
            ),
        )
    )

    requests = await client.providers.list_caqh_import_requests(CaqhImportRequestListParams(provider="p-1"))
    assert len(requests) == 1
    assert requests[0].id == 1
    assert requests[0].full_name == "Jane Doe"


@pytest.mark.asyncio
async def test_get_org_joining_date(client, mock_api):
    mock_api.get(_ORG_JOINING_DATE_URL).mock(
        return_value=httpx.Response(200, json={"id": "prof-1", "org_joining_date": "2024-01-15"})
    )

    record = await client.providers.get_org_joining_date("prof-1")
    assert record.id == "prof-1"
    assert record.org_joining_date is not None
    assert record.org_joining_date.isoformat() == "2024-01-15"


@pytest.mark.asyncio
async def test_update_org_joining_date(client, mock_api):
    import datetime
    import json

    route = mock_api.patch(_ORG_JOINING_DATE_URL).mock(
        return_value=httpx.Response(200, json={"id": "prof-1", "org_joining_date": "2025-06-01"})
    )

    record = await client.providers.update_org_joining_date("prof-1", datetime.date(2025, 6, 1))
    assert record.org_joining_date == datetime.date(2025, 6, 1)

    sent = json.loads(route.calls.last.request.content)
    assert sent == {"org_joining_date": "2025-06-01"}


@pytest.mark.asyncio
async def test_add_to_practice_location(client, mock_api):
    mock_api.post(_PRACTICE_LOC_PROVIDERS_URL).mock(
        return_value=httpx.Response(
            201,
            json={"message": "Practice Location Provider associations created successfully"},
        )
    )

    result = await client.providers.add_to_practice_location(
        PracticeLocationProvidersCreate(providers=["p-1", "p-2"], practice_location="loc-1")
    )
    assert result["message"] == "Practice Location Provider associations created successfully"
