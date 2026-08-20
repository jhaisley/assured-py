"""Task models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

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


class ExpirableUpdate(BaseModel):
    """Payload to partially update an expirable task (``PATCH .../expirables/{task_id}/``)."""

    archived: bool | None = None


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
    assignee_user_type: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    client_details: ClientDetails | None = None
    client: str | None = None
    client_name: str | None = None
    created_by: str | None = None
    created_by_name: str | None = None
    last_updated_by: str | None = None
    last_updated_by_first_name: str | None = None
    last_updated_by_last_name: str | None = None
    task_type: str | None = None
    facility: str | None = None
    facility_name: str | None = None
    creation_source: str | None = None
    file: str | None = None
    archived: bool | None = None
    current_owner: str | None = None
    current_owner_details: dict[str, Any] | None = None
    latest_task_timeline_updated_at: datetime | None = None
    latest_task_timeline_updated_by: str | None = None
    latest_task_timeline_updated_by_first_name: str | None = None
    latest_task_timeline_updated_by_last_name: str | None = None
    target_instance_metadata: str | None = None
    target_instance_id: str | None = None
    target_model_name: str | None = None
    task_timelines: list[dict[str, Any]] | None = None


class TaskCreate(BaseModel):
    """Payload to create a task.

    ``status`` values: PENDING, IN_PROGRESS, COMPLETED, CANCELLED.
    ``task_type`` values: INCOMPLETE_PROFILE, INFORMATION_REQUIRED, CREDENTIALING_REQUEST, SIGNATURE.
    """

    name: str
    description: str | None = None
    status: str | None = None
    due_on: datetime | None = None
    assignee: str | None = None
    task_type: str | None = None
    facility: str | None = None


class TaskListParams(BaseModel):
    """Query parameters for the task list."""

    assignee: str | None = None
    assignee_in: str | None = None
    assignee_user_type: str | None = None
    client: str | None = None
    client_in: str | None = None
    created_at_after: datetime | None = None
    created_at_before: datetime | None = None
    created_by: str | None = None
    created_by_in: str | None = None
    current_owner: str | None = None
    due_on_after: datetime | None = None
    due_on_before: datetime | None = None
    enrollment_request: str | None = None
    facility: str | None = None
    facility_in: str | None = None
    is_facility_task: bool | None = None
    latest_task_timeline_updated_at_after: datetime | None = None
    latest_task_timeline_updated_at_before: datetime | None = None
    latest_task_timeline_updated_by: str | None = None
    latest_task_timeline_updated_by_in: str | None = None
    limit: int | None = None
    offset: int | None = None
    ordering: str | None = None
    search: str | None = None
    status: str | None = None
    status_in: str | None = None
    task_type: str | None = None
    task_type_in: str | None = None
    updated_at_after: datetime | None = None
    updated_at_before: datetime | None = None


class TaskTimeline(BaseModel):
    """A timeline entry for a task."""

    id: str | None = None
    action: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    log_type: str | None = None
    updated_at: datetime | None = None
    updated_by: dict[str, Any] | str | None = None
    status: str | None = None
    current_owner: str | None = None
    current_owner_name: str | None = None
    note: str | None = None
    attachments_url: str | None = None
    due_on: datetime | None = None
    archived: bool | None = None
