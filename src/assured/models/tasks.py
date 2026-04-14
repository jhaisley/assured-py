"""Task models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from assured.models.common import ClientDetails


class ExpirableTask(BaseModel):
    """An expirable task."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    due_on: datetime | None = None
    last_updated_by_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    assignee: str | None = None
    assignee_name: str | None = None
    archived: bool | None = None
    client_details: ClientDetails | None = None


class ExpirableListParams(BaseModel):
    """Query parameters for expirable tasks."""

    archived: bool | None = None
    assignee: str | None = None
    client_ids: str | None = None
    created_at_after: datetime | None = None
    created_at_before: datetime | None = None
    due_on_after: datetime | None = None
    due_on_before: datetime | None = None
    limit: int | None = None
    offset: int | None = None
    ordering: str | None = None
    search: str | None = None
    updated_at_after: datetime | None = None
    updated_at_before: datetime | None = None


class Task(BaseModel):
    """A general task."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None
    due_on: datetime | None = None
    assignee: str | None = None
    assignee_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    client_details: ClientDetails | None = None


class TaskCreate(BaseModel):
    """Payload to create a task."""

    name: str
    description: str | None = None
    due_on: datetime | None = None
    assignee: str | None = None


class TaskListParams(BaseModel):
    """Query parameters for the task list."""

    limit: int | None = None
    offset: int | None = None
    ordering: str | None = None
    search: str | None = None


class TaskTimeline(BaseModel):
    """A timeline entry for a task."""

    id: str | None = None
    action: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None
