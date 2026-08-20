"""Tests for the payer enrollment resource."""

from __future__ import annotations

import json

import httpx
import pytest

from assured.models.payer_enrollment import (
    BulkOaAssignment,
    EnrollmentRequestStatusUpdate,
    EnrollmentTimelineParams,
    ExistingGroupEnrollmentCreate,
    ExistingProviderEnrollmentCreate,
)
from tests.conftest import paginated_response

_BASE = "https://test-api.example.com/api/v1/payer-enrollment"
_DETAIL_URL = f"{_BASE}/enrollment-request-detail/req-1/"
_UPDATE_STATUS_URL = f"{_BASE}/enrollment-request-update-status/req-1/"
_TIMELINE_URL = f"{_BASE}/enrollment-request-timeline/"
_ADD_GROUP_URL = f"{_BASE}/add-existing-group-enrollment/"
_ADD_PROVIDER_URL = f"{_BASE}/add-existing-provider-enrollment/"
_BULK_OA_URL = f"{_BASE}/self-serve/bulk-oa-assignment/"
_SELECTABLE_OA_URL = f"{_BASE}/payer-enrollment-request-reassignment-selectable-oa-users-list/"


@pytest.mark.asyncio
async def test_get_request_detail(client, mock_api):
    mock_api.get(_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "req-1",
                "request_id": "PE-0001",
                "enrollment_type": "PROVIDER",
                "status": "SUBMITTED",
                "created_at": "2026-07-16T11:36:10.167Z",
                "health_plan_name": "Acme Health",
                "state": "MD",
                "retrigger_attempts": 2,
                "group_providers": [{"id": "prov-1", "full_name": "Doc Test"}],
                "oa_actions_available": {"can_update": True, "can_view": True},
                "billing_enabled": True,
            },
        )
    )

    detail = await client.payer_enrollment.get_request_detail("req-1")
    assert detail.id == "req-1"
    assert detail.status == "SUBMITTED"
    assert detail.created_at.year == 2026
    assert detail.group_providers[0].full_name == "Doc Test"
    assert detail.oa_actions_available["can_update"] is True


@pytest.mark.asyncio
async def test_update_request_status(client, mock_api):
    route = mock_api.patch(_UPDATE_STATUS_URL).mock(
        return_value=httpx.Response(
            200,
            json={"status": "CANCELLED", "proof_of_documents": []},
        )
    )

    result = await client.payer_enrollment.update_request_status(
        "req-1",
        EnrollmentRequestStatusUpdate(status="CANCELLED", status_reason="DUPLICATE_REQUEST"),
    )
    assert result["status"] == "CANCELLED"
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"status": "CANCELLED", "status_reason": "DUPLICATE_REQUEST"}


@pytest.mark.asyncio
async def test_list_enrollment_timeline(client, mock_api):
    mock_api.get(_TIMELINE_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {
                        "id": "tl-1",
                        "enrollment_request": "req-1",
                        "change_type": "STATUS_CHANGE",
                        "status": "SUBMITTED",
                        "created_at": "2026-07-16T11:36:10.167Z",
                        "updated_by_full_name": "Ops Analyst",
                        "proof_of_documents": ["doc-1"],
                    },
                ]
            ),
        )
    )

    entries = await client.payer_enrollment.list_enrollment_timeline(
        EnrollmentTimelineParams(enrollment_request="req-1")
    )
    assert len(entries) == 1
    assert entries[0].change_type == "STATUS_CHANGE"
    assert entries[0].updated_by_full_name == "Ops Analyst"


@pytest.mark.asyncio
async def test_list_enrollment_timeline_df(client, mock_api):
    mock_api.get(_TIMELINE_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "tl-1", "enrollment_request": "req-1", "change_type": "NEW_FOLLOWUP"},
                ]
            ),
        )
    )

    df = await client.payer_enrollment.list_enrollment_timeline_df()
    assert len(df) == 1
    assert "change_type" in df.columns


@pytest.mark.asyncio
async def test_add_existing_group_enrollment(client, mock_api):
    mock_api.post(_ADD_GROUP_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "ge-1",
                "tax_entity": "te-1",
                "state": "MD",
                "health_plan": "hp-1",
                "primary_practice_location": "loc-1",
                "par_status": "PAR",
                "client": "client-1",
                "effective_date": "2026-01-01",
            },
        )
    )

    result = await client.payer_enrollment.add_existing_group_enrollment(
        ExistingGroupEnrollmentCreate(
            tax_entity="te-1",
            state="MD",
            health_plan="hp-1",
            primary_practice_location="loc-1",
            par_status="PAR",
            client="client-1",
        )
    )
    assert result.id == "ge-1"
    assert result.state == "MD"


@pytest.mark.asyncio
async def test_add_existing_provider_enrollment(client, mock_api):
    mock_api.post(_ADD_PROVIDER_URL).mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "pe-1",
                "provider": "prov-1",
                "tax_entity": "te-1",
                "state": "MD",
                "health_plan": "hp-1",
                "primary_practice_location": "loc-1",
                "par_status": "PAR",
                "client": "client-1",
            },
        )
    )

    result = await client.payer_enrollment.add_existing_provider_enrollment(
        ExistingProviderEnrollmentCreate(
            provider="prov-1",
            tax_entity="te-1",
            state="MD",
            health_plan="hp-1",
            primary_practice_location="loc-1",
            par_status="PAR",
            client="client-1",
        )
    )
    assert result.id == "pe-1"
    assert result.client == "client-1"


@pytest.mark.asyncio
async def test_bulk_oa_assignment(client, mock_api):
    route = mock_api.post(_BULK_OA_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "message": "2 requests assigned",
                "assigned_oas_data": [{"id": "oa-1", "count": 2, "first_name": "Ops"}],
            },
        )
    )

    result = await client.payer_enrollment.bulk_oa_assignment(
        BulkOaAssignment(
            oas_to_assign=["oa-1"],
            request_phase=["SUBMISSION_PHASE"],
            states=["MD"],
        )
    )
    assert result["message"] == "2 requests assigned"
    sent = json.loads(route.calls.last.request.content)
    assert sent["oas_to_assign"] == ["oa-1"]
    assert sent["request_phase"] == ["SUBMISSION_PHASE"]


@pytest.mark.asyncio
async def test_list_reassignment_selectable_oa_users(client, mock_api):
    route = mock_api.get(_SELECTABLE_OA_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "oa-1", "oa_full_name": "Ops Analyst"},
                ]
            ),
        )
    )

    users = await client.payer_enrollment.list_reassignment_selectable_oa_users("req-1", search="Ops")
    assert len(users) == 1
    assert users[0].oa_full_name == "Ops Analyst"
    sent_url = route.calls.last.request.url
    assert sent_url.params["enrollment_request"] == "req-1"
    assert sent_url.params["search"] == "Ops"
