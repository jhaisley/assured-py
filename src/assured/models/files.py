"""File handling models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class StorageMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    storage_backend: str | None = None
    storage_backend_class: str | None = None
    bucket_name: str | None = None
    region: str | None = None
    endpoint_url: str | None = None
    custom_domain: str | None = None
    credential_profile: str | None = None
    media_root: str | None = None
    use_s3_for_media: bool | None = None
    acl: str | None = None
    signature_version: str | None = None
    file_overwrite: bool | None = None
    querystring_auth: bool | None = None
    object_parameters: dict[str, Any] | None = None
    original_filename: str | None = None
    content_type: str | None = None
    file_size_bytes: int | None = None
    upload_path: str | None = None
    uploaded_by_user_id: str | None = None
    uploaded_by_client_id: str | None = None
    s3_object_url: str | None = None
    s3_uri: str | None = None
    django_env: str | None = None
    debug_mode: bool | None = None
    uploaded_file_url: str | None = None
    uploaded_file_uri: str | None = None


class FileRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    file: str | None = None
    file_url: str | None = None
    name: str | None = None
    created_at: datetime | None = None
    storage_metadata: StorageMetadata | None = None
    uploaded_file_uri: str | None = None


class PresignedUrlResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    presigned_url: str
