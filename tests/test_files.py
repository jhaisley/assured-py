"""Tests for the Files undocumented endpoints."""

import httpx
import pytest
import respx

from assured.client import AssuredClient
from assured.settings import Settings


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        base_url="https://api.assured.test",
        api_key="test-api-key",
        user="dev@test.com",
        **{"assured_pass": "password123"},
    )


@pytest.mark.asyncio
async def test_file_upload(mock_settings: Settings) -> None:
    async with AssuredClient(settings=mock_settings) as client:
        with respx.mock(assert_all_called=True) as mocker:
            # Login first (lazy triggered)
            mocker.post("https://api.assured.test/api/v1/users/login/").mock(
                return_value=httpx.Response(200, json={"data": {"jwt": {"access": "mock-jwt"}}})
            )

            # File upload endpoint
            mock_upload = mocker.post("https://api.assured.test/api/v1/files/handle/").mock(
                return_value=httpx.Response(
                    201,
                    json={
                        "id": "mock-uuid",
                        "file": "https://s3.amazonaws.../mock.pdf",
                        "file_url": "s3://assured-bots/mock.pdf",
                        "name": "random-name.pdf",
                        "created_at": "2026-04-10T12:00:00Z",
                    },
                )
            )

            record = await client.files.upload(b"fake-pdf-content", "mock.pdf")

            assert record.id == "mock-uuid"
            assert record.name == "random-name.pdf"

            # Ensure JWT is attached and multipart format is used
            req = mock_upload.calls.last.request
            assert req.headers["Authorization"] == "Bearer mock-jwt"
            assert req.headers["Content-Type"].startswith("multipart/form-data")

            # Ensure file is in multipart content
            body = req.read().decode("latin1")
            assert "fake-pdf-content" in body


@pytest.mark.asyncio
async def test_presign_url(mock_settings: Settings) -> None:
    async with AssuredClient(settings=mock_settings) as client:
        with respx.mock(assert_all_called=True) as mocker:
            # Login
            mocker.post("https://api.assured.test/api/v1/users/login/").mock(
                return_value=httpx.Response(200, json={"data": {"jwt": {"access": "mock-jwt"}}})
            )

            # Presigned URL endpoint
            mock_presign = mocker.post("https://api.assured.test/api/v1/files/presign-s3-url/presign_s3_url/").mock(
                return_value=httpx.Response(200, json={"presigned_url": "https://s3.test/presigned?token=123"})
            )

            url = await client.files.presign_url("s3://assured-bots/mock.pdf")

            assert url == "https://s3.test/presigned?token=123"

            # Verify payload
            req = mock_presign.calls.last.request
            assert req.headers["Authorization"] == "Bearer mock-jwt"
            import json

            payload = json.loads(req.read())
            assert payload["s3_url"] == "s3://assured-bots/mock.pdf"
            assert payload["presigned_url"] == ""
