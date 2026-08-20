"""Tests for the credentialing resource."""

from __future__ import annotations

import json

import httpx
import pytest

from assured.models.credentialing import (
    ApprovalLetterSend,
    CloseRequestItem,
    CredentialingRequestCreate,
)
from tests.conftest import paginated_response

_LIST_URL = "https://test-api.example.com/api/v1/credentialing/request-list/"
_CREATE_URL = "https://test-api.example.com/api/v1/credentialing/create-credentialing-request/"
_DETAIL_URL = "https://test-api.example.com/api/v1/credentialing/request-detail/req-123/"
_PACKETS_URL = "https://test-api.example.com/api/v1/credentialing/credentialing-packets/"
_PACKET_DETAIL_URL = "https://test-api.example.com/api/v1/credentialing/credentialing-packets/pkt-1/"
_NEED_ACTION_URL = "https://test-api.example.com/api/v1/credentialing/credentialing-need-action-list/"
_MONITORING_URL = "https://test-api.example.com/api/v1/credentialing/monitoring-packet-events-list/"
_OVERVIEW_URL = "https://test-api.example.com/api/v1/credentialing/provider-credentialing-overview/prov-1/"
_PROVIDERS_STATES_URL = "https://test-api.example.com/api/v1/credentialing/providers-for-credentialing-with-states/"
_CLOSE_URL = "https://test-api.example.com/api/v1/credentialing/close-request/"
_DOWNLOAD_URL = "https://test-api.example.com/api/v1/credentialing/credentialing-download/"
_APPROVAL_DETAIL_URL = "https://test-api.example.com/api/v1/clients/credentialing-approval-letter-detail/req-123/"
_SEND_APPROVAL_URL = "https://test-api.example.com/api/v1/clients/credentialing-send-approval-letter/"


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


@pytest.mark.asyncio
async def test_list_packets(client, mock_api):
    mock_api.get(_PACKETS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "pkt-1",
                        "credentialing_request": "req-1",
                        "credentialing_status": "CREDENTIALED",
                        "packet_status": "CLEAR",
                        "credentialing_date": "2026-01-15T00:00:00Z",
                        "states": "MD, VA",
                        "provider": "prov-1",
                    },
                ]
            ),
        )
    )

    packets = await client.credentialing.list_packets()
    assert len(packets) == 1
    assert packets[0].credentialing_status == "CREDENTIALED"
    assert packets[0].packet_status == "CLEAR"


@pytest.mark.asyncio
async def test_get_packet(client, mock_api):
    mock_api.get(_PACKET_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "pkt-1",
                "credentialing_request": "req-1",
                "credentialing_status": "TERMINATED",
                "packet_status": "CONCERN",
                "recredentialing_date": "2027-01-15T00:00:00Z",
            },
        )
    )

    packet = await client.credentialing.get_packet("pkt-1")
    assert packet.id == "pkt-1"
    assert packet.credentialing_status == "TERMINATED"
    assert packet.recredentialing_date.year == 2027


@pytest.mark.asyncio
async def test_list_packets_df(client, mock_api):
    mock_api.get(_PACKETS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response([{"id": "pkt-1", "packet_status": "CLEAR"}]),
        )
    )

    df = await client.credentialing.list_packets_df()
    assert len(df) == 1
    assert "packet_status" in df.columns


@pytest.mark.asyncio
async def test_list_need_actions(client, mock_api):
    mock_api.get(_NEED_ACTION_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "req-9",
                        "status": "IN_PROGRESS",
                        "credentialing_type": "RE_CREDENTIALING",
                        "sla_days": 12,
                        "state_codes": ["MD"],
                        "assignee_details": {"id": "u-1", "email": "verifier@test.com", "first_name": "Vera"},
                        "provider_details": {"id": "prov-1", "email": "doc@test.com", "org_joining_date": "2024-02-01"},
                        "verification_event_tasks": [{"type": "LICENSE", "status": "PENDING"}],
                    },
                ]
            ),
        )
    )

    items = await client.credentialing.list_need_actions()
    assert len(items) == 1
    assert items[0].sla_days == 12
    assert items[0].assignee_details.email == "verifier@test.com"
    assert items[0].provider_details.org_joining_date == "2024-02-01"


@pytest.mark.asyncio
async def test_list_monitoring_events(client, mock_api):
    mock_api.get(_MONITORING_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "evt-1",
                        "type": "LICENSE_MONITORING",
                        "source": "OA",
                        "result": "CONCERN",
                        "psv_field": "license_status",
                        "psv_val": "EXPIRED",
                        "oa_verified_at": "2026-08-01T10:00:00Z",
                        "provider_details": {"id": "prov-1", "individual_npi": "1234567890"},
                        "monitoring_concern_notes": "License expired.",
                    },
                ]
            ),
        )
    )

    events = await client.credentialing.list_monitoring_events(result="CONCERN")
    assert len(events) == 1
    assert events[0].result == "CONCERN"
    assert events[0].provider_details.individual_npi == "1234567890"


@pytest.mark.asyncio
async def test_get_provider_overview(client, mock_api):
    mock_api.get(_OVERVIEW_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "prov-1",
                "email": "doc@test.com",
                "provider_type": "MD",
                "org_joining_date": "2024-02-01",
                "last_credentialing_request": {
                    "id": "req-1",
                    "status": "CLEAR",
                    "state_codes": ["MD", "VA"],
                    "approver_name": "Dr. Approver",
                },
                "last_packet": {
                    "id": "pkt-1",
                    "credentialing_status": "CREDENTIALED",
                    "states": ["MD", "VA"],
                },
            },
        )
    )

    overview = await client.credentialing.get_provider_overview("prov-1")
    assert overview.email == "doc@test.com"
    assert overview.last_credentialing_request.status == "CLEAR"
    assert overview.last_packet.credentialing_status == "CREDENTIALED"


@pytest.mark.asyncio
async def test_list_providers_for_credentialing(client, mock_api):
    mock_api.get(_PROVIDERS_STATES_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "prov-1",
                        "email": "doc@test.com",
                        "first_name": "Doc",
                        "last_name": "Test",
                        "states_selector": ["MD", "VA"],
                    },
                ]
            ),
        )
    )

    providers = await client.credentialing.list_providers_for_credentialing(search="doc")
    assert len(providers) == 1
    assert providers[0].states_selector == ["MD", "VA"]


@pytest.mark.asyncio
async def test_close_request(client, mock_api):
    route = mock_api.patch(_CLOSE_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "CANCELLED",
                "closure_remarks": "Duplicate request",
                "request_closed_by": "user-1",
            },
        )
    )

    result = await client.credentialing.close_request(
        [
            CloseRequestItem(
                id="req-1",
                reason="DUPLICATE_CREDENTIALING_REQUEST",
                closure_remarks="Duplicate request",
                request_closed_by="user-1",
            )
        ]
    )
    assert result["status"] == "CANCELLED"

    sent = json.loads(route.calls.last.request.content)
    assert isinstance(sent, list)
    assert sent[0]["id"] == "req-1"
    assert sent[0]["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_download_packets(client, mock_api):
    mock_api.post(_DOWNLOAD_URL).mock(
        return_value=httpx.Response(
            200,
            json={"credentialing_request_ids": ["req-1", "req-2"]},
        )
    )

    result = await client.credentialing.download_packets(["req-1", "req-2"])
    assert result["credentialing_request_ids"] == ["req-1", "req-2"]


@pytest.mark.asyncio
async def test_get_approval_letter(client, mock_api):
    mock_api.get(_APPROVAL_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "cc_emails": ["admin@test.com"],
                "recipient_email": "doc@test.com",
                "last_sent_status": "SENT",
                "last_sent_date": "2026-08-01T09:00:00Z",
                "html_preview": "<p>Congrats</p>",
                "markdown_preview": "Congrats",
            },
        )
    )

    letter = await client.credentialing.get_approval_letter("req-123")
    assert letter.recipient_email == "doc@test.com"
    assert letter.cc_emails == ["admin@test.com"]
    assert letter.last_sent_date.month == 8


@pytest.mark.asyncio
async def test_send_approval_letter(client, mock_api):
    mock_api.post(_SEND_APPROVAL_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "letter-1",
                "provider_name": "Doc Test",
                "sent_to": "doc@test.com",
                "status": "PENDING",
            },
        )
    )

    result = await client.credentialing.send_approval_letter(
        ApprovalLetterSend(
            client="client-1",
            provider="prov-1",
            request="req-123",
            additional_cc_emails=["admin@test.com"],
        )
    )
    assert result["id"] == "letter-1"
    assert result["status"] == "PENDING"
