"""Tests for the credentialing resource."""

from __future__ import annotations

import httpx
import pytest

from assured.models.credentialing import CredentialingRequestCreate
from tests.conftest import paginated_response

_LIST_URL = "https://test-api.example.com/api/v1/credentialing/request-list/"
_CREATE_URL = "https://test-api.example.com/api/v1/credentialing/create-credentialing-request/"
_DETAIL_URL = "https://test-api.example.com/api/v1/credentialing/request-detail/req-123/"


@pytest.mark.asyncio
async def test_list_credentialing_requests(client, mock_api):
    mock_api.get(_LIST_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "req-1",
                        "status": "PENDING",
                        "credentialing_type": "INITIAL_CREDENTIALING",
                        "state_codes": ["MD", "VA"],
                    },
                ]
            ),
        )
    )

    reqs = await client.credentialing.list_requests()
    assert len(reqs) == 1
    assert reqs[0].status == "PENDING"
    assert "MD" in reqs[0].state_codes


@pytest.mark.asyncio
async def test_create_credentialing_request(client, mock_api):
    mock_api.post(_CREATE_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "new-req",
                "provider": "prov-1",
                "status": "PENDING",
                "credentialing_type": "INITIAL_CREDENTIALING",
            },
        )
    )

    result = await client.credentialing.create_request(
        CredentialingRequestCreate(provider="prov-1", state_codes=["MD"])
    )
    assert result["id"] == "new-req"


@pytest.mark.asyncio
async def test_get_credentialing_detail(client, mock_api):
    mock_api.get(_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "req-123",
                "status": "IN_PROGRESS",
                "credentialing_type": "INITIAL_CREDENTIALING",
                "provider_details": {
                    "id": "prov-1",
                    "email": "doc@test.com",
                    "first_name": "Doc",
                    "last_name": "Test",
                },
            },
        )
    )

    detail = await client.credentialing.get_request("req-123")
    assert detail.id == "req-123"
    assert detail.provider_details.email == "doc@test.com"


@pytest.mark.asyncio
async def test_list_credentialing_df(client, mock_api):
    mock_api.get(_LIST_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "r-1", "status": "PENDING", "credentialing_type": "INITIAL_CREDENTIALING"},
                ]
            ),
        )
    )

    df = await client.credentialing.list_requests_df()
    assert len(df) == 1
    assert "status" in df.columns
