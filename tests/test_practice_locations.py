"""Tests for the practice locations resource."""

from __future__ import annotations

import httpx
import pytest

from assured.models.practice_locations import (
    PracticeLocationProviderListParams,
    ProviderPracticeLocationsBulkCreate,
)
from assured.models.providers import PracticeLocationProvidersCreate
from tests.conftest import paginated_response

_LOCATIONS_URL = "https://test-api.example.com/api/v1/clients/practice-locations/"
_LOCATION_DETAIL_URL = "https://test-api.example.com/api/v1/clients/practice-locations/loc-1/"
_PROVIDER_LIST_URL = "https://test-api.example.com/api/v1/users/practice-location-provider/"
_PROVIDER_DETAIL_URL = "https://test-api.example.com/api/v1/users/practice-location-provider/assoc-1/"
_PROVIDER_CREATE_URL = "https://test-api.example.com/api/v1/users/practice-location-providers/"
_PROVIDER_BULK_URL = "https://test-api.example.com/api/v1/users/provider-practice-locations-bulk/"
_MARK_PRIMARY_URL = "https://test-api.example.com/api/v1/users/mark-primary-practice-location/assoc-1/"


@pytest.mark.asyncio
async def test_list_practice_locations_is_archived_filter(client, mock_api):
    route = mock_api.get(_LOCATIONS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "loc-1", "name": "Main Clinic", "mailing_state": "CA"},
                ]
            ),
        )
    )

    locations = await client.practice_locations.list(is_archived=False)
    assert len(locations) == 1
    assert locations[0].name == "Main Clinic"
    assert locations[0].mailing_state == "CA"
    assert "is_archived=false" in str(route.calls.last.request.url).lower()


@pytest.mark.asyncio
async def test_get_practice_location_new_fields(client, mock_api):
    mock_api.get(_LOCATION_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "loc-1",
                "name": "Main Clinic",
                "archived_at": "2026-01-15T10:30:00Z",
                "mailing_state": "TX",
            },
        )
    )

    location = await client.practice_locations.get("loc-1")
    assert location.id == "loc-1"
    assert location.archived_at is not None
    assert location.archived_at.year == 2026
    assert location.mailing_state == "TX"


@pytest.mark.asyncio
async def test_list_providers(client, mock_api):
    mock_api.get(_PROVIDER_LIST_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "assoc-1",
                        "practice_location": "loc-1",
                        "provider": "prov-1",
                        "provider_name": "Dr. Smith",
                        "practice_location_name": "Main Clinic",
                        "is_primary_location": True,
                    },
                ]
            ),
        )
    )

    associations = await client.practice_locations.list_providers(
        PracticeLocationProviderListParams(provider="prov-1")
    )
    assert len(associations) == 1
    assert associations[0].provider_name == "Dr. Smith"
    assert associations[0].is_primary_location is True


@pytest.mark.asyncio
async def test_get_provider(client, mock_api):
    mock_api.get(_PROVIDER_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "assoc-1",
                "practice_location": "loc-1",
                "provider": "prov-1",
                "state": "CA",
                "npi": "1234567890",
                "archived_at": None,
            },
        )
    )

    association = await client.practice_locations.get_provider("assoc-1")
    assert association.id == "assoc-1"
    assert association.npi == "1234567890"
    assert association.archived_at is None


@pytest.mark.asyncio
async def test_delete_provider(client, mock_api):
    mock_api.delete(_PROVIDER_DETAIL_URL).mock(return_value=httpx.Response(204))

    result = await client.practice_locations.delete_provider("assoc-1")
    assert result is None


@pytest.mark.asyncio
async def test_create_provider(client, mock_api):
    route = mock_api.post(_PROVIDER_CREATE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"providers": ["prov-1", "prov-2"], "practice_location": "loc-1"},
        )
    )

    result = await client.practice_locations.create_provider(
        PracticeLocationProvidersCreate(providers=["prov-1", "prov-2"], practice_location="loc-1")
    )
    assert result["practice_location"] == "loc-1"
    assert result["providers"] == ["prov-1", "prov-2"]
    assert route.called


@pytest.mark.asyncio
async def test_create_provider_locations_bulk(client, mock_api):
    mock_api.post(_PROVIDER_BULK_URL).mock(
        return_value=httpx.Response(
            201,
            json={"message": "Created", "created_count": 2, "skipped_count": 1},
        )
    )

    result = await client.practice_locations.create_provider_locations_bulk(
        ProviderPracticeLocationsBulkCreate(provider="prov-1", practice_locations=["loc-1", "loc-2", "loc-3"])
    )
    assert result["created_count"] == 2
    assert result["skipped_count"] == 1


@pytest.mark.asyncio
async def test_mark_primary(client, mock_api):
    route = mock_api.patch(_MARK_PRIMARY_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "assoc-1",
                "practice_location": "loc-1",
                "provider": "prov-1",
                "is_primary_location": True,
            },
        )
    )

    association = await client.practice_locations.mark_primary("assoc-1")
    assert association.id == "assoc-1"
    assert association.is_primary_location is True
    assert route.calls.last.request.content == b'{"is_primary_location":true}'
