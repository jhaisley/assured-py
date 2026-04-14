"""Files resource for undocumented endpoint coverage."""

from __future__ import annotations

import mimetypes
import os
import uuid
from typing import TYPE_CHECKING

from assured.models.files import FileRecord, PresignedUrlResponse

if TYPE_CHECKING:
    from assured.client import AssuredClient

_HANDLE_PATH = "/api/v1/files/handle/"
_PRESIGN_PATH = "/api/v1/files/presign-s3-url/presign_s3_url/"


class FilesResource:
    """Operations on file storage and presigning."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    async def upload(self, file_content: bytes, filename: str, mime_type: str | None = None) -> FileRecord:
        """Upload a file to the Assured platform via its undocumented handle endpoint.

        Note: This utilizes a JSON Web Token explicitly rather than the API Key.

        Args:
            file_content: The raw bytes of the file you are uploading.
            filename: The original filename strings.
            mime_type: File content type, defaults to mimetypes.guess_type or octet-stream.

        Returns:
            FileRecord detailing the UUID object ID along with mapped S3 URIs.
        """
        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(filename)
            mime_type = mime_type or "application/octet-stream"

        ext = os.path.splitext(filename)[1]
        generated_name = f"{uuid.uuid4()}{ext}"

        data = {"name": generated_name}
        files = {"file": (filename, file_content, mime_type)}

        resp = await self._client._post(_HANDLE_PATH, data=data, files=files, requires_jwt=True)
        return FileRecord.model_validate(resp)

    async def presign_url(self, s3_url: str) -> str:
        """Exchange an internal S3 URL for a publicly accessible presigned URL.

        Note: This utilizes a JSON Web Token explicitly rather than the API Key.

        Args:
            s3_url: A target URI starting with `s3://` (found in the `FileRecord` responses)

        Returns:
            A string containing the short-lived presigned URL.
        """
        payload = {
            "s3_url": s3_url,
            "presigned_url": "",
        }
        resp = await self._client._post(_PRESIGN_PATH, json=payload, requires_jwt=True)
        return PresignedUrlResponse.model_validate(resp).presigned_url
