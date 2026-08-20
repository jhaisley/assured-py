"""Credentialing resource."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.credentialing import (
    ApprovalLetterDetail,
    ApprovalLetterSend,
    CloseRequestItem,
    CredentialingListParams,
    CredentialingNeedAction,
    CredentialingNeedActionListParams,
    CredentialingPacket,
    CredentialingPacketListParams,
    CredentialingRequest,
    CredentialingRequestCreate,
    CredentialingRequestDetail,
    MonitoringPacketEvent,
    MonitoringPacketEventListParams,
    ProviderCredentialingOverview,
    ProviderWithStates,
    ProviderWithStatesListParams,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_CREATE_PATH = "/api/v1/credentialing/create-credentialing-request/"
_DETAIL_PATH = "/api/v1/credentialing/request-detail/{id}/"
_LIST_PATH = "/api/v1/credentialing/request-list/"
_PACKETS_PATH = "/api/v1/credentialing/credentialing-packets/"
_PACKET_DETAIL_PATH = "/api/v1/credentialing/credentialing-packets/{id}/"
_NEED_ACTION_PATH = "/api/v1/credentialing/credentialing-need-action-list/"
_MONITORING_EVENTS_PATH = "/api/v1/credentialing/monitoring-packet-events-list/"
_PROVIDER_OVERVIEW_PATH = "/api/v1/credentialing/provider-credentialing-overview/{id}/"
_PROVIDERS_WITH_STATES_PATH = "/api/v1/credentialing/providers-for-credentialing-with-states/"
_CLOSE_REQUEST_PATH = "/api/v1/credentialing/close-request/"
_DOWNLOAD_PATH = "/api/v1/credentialing/credentialing-download/"
_APPROVAL_LETTER_DETAIL_PATH = "/api/v1/clients/credentialing-approval-letter-detail/{cred_request_id}/"
_SEND_APPROVAL_LETTER_PATH = "/api/v1/clients/credentialing-send-approval-letter/"


class CredentialingResource:
    """Operations on credentialing requests."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def create_request(self, data: CredentialingRequestCreate) -> dict[str, Any]:
        """Create a new credentialing request."""
        return await self._client._post(_CREATE_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def get_request(self, request_id: str) -> CredentialingRequestDetail:
        """Get the detail/status of a credentialing request."""
        path = _DETAIL_PATH.format(id=request_id)
        data = await self._client._get(path)
        return CredentialingRequestDetail.model_validate(data)

    async def list_requests(
        self, params: CredentialingListParams | None = None, **kwargs: Any
    ) -> list[CredentialingRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_LIST_PATH, params=raw_params)
        return [CredentialingRequest.model_validate(item) for item in data.get("results", [])]

    async def list_requests_all(
        self, params: CredentialingListParams | None = None, **kwargs: Any
    ) -> list[CredentialingRequest]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return [CredentialingRequest.model_validate(item) for item in records]

    async def list_requests_df(self, params: CredentialingListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_LIST_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    # ---- Credentialing Packets ----

    async def list_packets(
        self, params: CredentialingPacketListParams | None = None, **kwargs: Any
    ) -> list[CredentialingPacket]:
        """List credentialing packets (single page).

        Args:
            params: Optional filter/pagination parameters.
            **kwargs: Extra query parameters merged over ``params``.

        Returns:
            The packets from one page of results.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PACKETS_PATH, params=raw_params)
        return [CredentialingPacket.model_validate(item) for item in data.get("results", [])]

    async def list_packets_all(
        self, params: CredentialingPacketListParams | None = None, **kwargs: Any
    ) -> list[CredentialingPacket]:
        """List all credentialing packets, auto-paginating through every page."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PACKETS_PATH, params=raw_params)
        return [CredentialingPacket.model_validate(item) for item in records]

    async def list_packets_df(self, params: CredentialingPacketListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        """Return all credentialing packets as a pandas DataFrame."""
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_PACKETS_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_packet(self, packet_id: str) -> CredentialingPacket:
        """Get a single credentialing packet by id."""
        path = _PACKET_DETAIL_PATH.format(id=packet_id)
        data = await self._client._get(path)
        return CredentialingPacket.model_validate(data)

    # ---- Need Action / Monitoring ----

    async def list_need_actions(
        self, params: CredentialingNeedActionListParams | None = None, **kwargs: Any
    ) -> list[CredentialingNeedAction]:
        """List credentialing requests that need action (single page).

        Args:
            params: Optional filter/pagination parameters.
            **kwargs: Extra query parameters merged over ``params``.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_NEED_ACTION_PATH, params=raw_params)
        return [CredentialingNeedAction.model_validate(item) for item in data.get("results", [])]

    async def list_monitoring_events(
        self, params: MonitoringPacketEventListParams | None = None, **kwargs: Any
    ) -> list[MonitoringPacketEvent]:
        """List monitoring packet events (single page).

        Args:
            params: Optional filter/pagination parameters.
            **kwargs: Extra query parameters merged over ``params``.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_MONITORING_EVENTS_PATH, params=raw_params)
        return [MonitoringPacketEvent.model_validate(item) for item in data.get("results", [])]

    # ---- Provider views ----

    async def get_provider_overview(self, provider_id: str) -> ProviderCredentialingOverview:
        """Get the credentialing overview for a provider."""
        path = _PROVIDER_OVERVIEW_PATH.format(id=provider_id)
        data = await self._client._get(path)
        return ProviderCredentialingOverview.model_validate(data)

    async def list_providers_for_credentialing(
        self, params: ProviderWithStatesListParams | None = None, **kwargs: Any
    ) -> list[ProviderWithStates]:
        """List providers eligible for credentialing, with their selectable states (single page).

        Args:
            params: Optional filter/pagination parameters (``id_in``, ``search``, ``limit``, ``offset``).
            **kwargs: Extra query parameters merged over ``params``.
        """
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_PROVIDERS_WITH_STATES_PATH, params=raw_params)
        return [ProviderWithStates.model_validate(item) for item in data.get("results", [])]

    # ---- Mutations ----

    async def close_request(self, items: list[CloseRequestItem]) -> dict[str, Any]:
        """Close (cancel) one or more credentialing requests.

        Args:
            items: One :class:`CloseRequestItem` per request to close.

        Returns:
            The raw API response describing the closure.
        """
        payload = [item.model_dump(mode="json", exclude_none=False) for item in items]
        return await self._client._patch(_CLOSE_REQUEST_PATH, json=payload)

    async def download_packets(self, credentialing_request_ids: list[str]) -> dict[str, Any]:
        """Request a download of credentialing packets for the given credentialing request ids.

        Args:
            credentialing_request_ids: Credentialing request UUIDs (from the request list).

        Returns:
            The raw API response (echoes ``credentialing_request_ids``).
        """
        payload = {"credentialing_request_ids": credentialing_request_ids}
        return await self._client._post(_DOWNLOAD_PATH, json=payload)

    # ---- Approval Letters ----

    async def get_approval_letter(self, cred_request_id: str) -> ApprovalLetterDetail:
        """Get the approval letter detail for a credentialing request."""
        path = _APPROVAL_LETTER_DETAIL_PATH.format(cred_request_id=cred_request_id)
        data = await self._client._get(path)
        return ApprovalLetterDetail.model_validate(data)

    async def send_approval_letter(self, data: ApprovalLetterSend) -> dict[str, Any]:
        """Send an approval letter to a provider.

        Args:
            data: The client, provider, and credentialing request UUIDs plus optional CC emails.

        Returns:
            The raw API response describing the sent letter.
        """
        return await self._client._post(_SEND_APPROVAL_LETTER_PATH, json=data.model_dump(mode="json", exclude_none=False))
