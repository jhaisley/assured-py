"""User models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    """A user account on the Assured platform."""

    id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    is_active: bool | None = None
    user_type: str | None = None
    date_joined: datetime | None = None
    email_verified_at: datetime | None = None
    activated_at: datetime | None = None
    deactivated_at: datetime | None = None


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
