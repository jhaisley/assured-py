"""User models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class User(BaseModel):
    """A user account on the Assured platform."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    is_active: bool | None = None
    user_type: str | None = None
    date_joined: datetime | None = None
    email_verified_at: datetime | None = None
    invited_at: datetime | None = None
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None
    source_of_joining: str | None = None
    client: str | None = None
    client_name: str | None = None


class UserListParams(BaseModel):
    """Query parameters for the users list endpoint."""

    is_active: bool | None = None
    limit: int | None = None
    offset: int | None = None
    ordering: str | None = None
    provider_profile__ready_for_credentialing: bool | None = None
    search: str | None = None
    user_type: str | None = None
    users_deactivated: bool | None = None
    users_invited: bool | None = None


class UserSlim(BaseModel):
    """A slim user record from ``GET /api/v1/users/user-list-slim/``."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    user_type: str | None = None


class UserSlimListParams(BaseModel):
    """Query parameters for the slim users list endpoint.

    ``user_type`` accepts values such as ``provider``, ``client_admin``, ``oa``,
    ``external_oa``, ``location_admin``, ``privilege_admin`` (see the API spec for
    the full enum). ``id_in`` / ``user_type_in`` take comma-separated values.
    """

    client: str | None = None
    id_in: str | None = None
    include_unverified: bool | None = None
    limit: int | None = None
    offset: int | None = None
    provider_profile__ready_for_credentialing: bool | None = None
    search: str | None = None
    user_type: str | None = None
    user_type_in: str | None = None


class LoggedInUserDetails(BaseModel):
    """Details of the currently authenticated user.

    Returned by ``GET /api/v1/users/logged-in-user-details/``. Nested objects
    (``provider_profile``, ``extra_data``, ``provider_profile_completion_info``,
    ``credentialing_readiness_info``) are kept as permissive dicts because their
    shapes are large and account-dependent.
    """

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    user_type: str | None = None
    is_active: bool | None = None
    provider_profile: dict[str, Any] | None = None
    extra_data: dict[str, Any] | None = None
    provider_profile_completion_info: dict[str, Any] | None = None
    user_associated_features: list[str] | None = None
    credentialing_readiness_info: dict[str, Any] | None = None
    assured_user_id: str | None = None
