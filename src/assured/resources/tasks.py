"""Tasks resource (tasks + expirables)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from assured.models.tasks import (
    ExpirableListParams,
    ExpirableTask,
    Task,
    TaskCreate,
    TaskListParams,
    TaskTimeline,
)

if TYPE_CHECKING:
    from assured.client import AssuredClient

_EXPIRABLES_PATH = "/api/v1/task-management/expirables/"
_TASKS_PATH = "/api/v1/task-management/tasks/"
_TASK_DETAIL_PATH = "/api/v1/task-management/tasks/{task_id}/"
_TASK_TIMELINE_PATH = "/api/v1/task-management/task-timelines/{task_id}/"


class TasksResource:
    """Operations on tasks and expirables."""

    def __init__(self, client: AssuredClient) -> None:
        self._client = client

    # ---- Expirables ----

    async def list_expirables(self, params: ExpirableListParams | None = None, **kwargs: Any) -> list[ExpirableTask]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_EXPIRABLES_PATH, params=raw_params)
        return [ExpirableTask.model_validate(item) for item in data.get("results", [])]

    async def list_expirables_all(
        self, params: ExpirableListParams | None = None, **kwargs: Any
    ) -> list[ExpirableTask]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_EXPIRABLES_PATH, params=raw_params)
        return [ExpirableTask.model_validate(item) for item in records]

    async def list_expirables_df(self, params: ExpirableListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_EXPIRABLES_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    # ---- Tasks ----

    async def create_task(self, data: TaskCreate) -> dict[str, Any]:
        """Create a new task."""
        return await self._client._post(_TASKS_PATH, json=data.model_dump(mode="json", exclude_none=False))

    async def list_tasks(self, params: TaskListParams | None = None, **kwargs: Any) -> list[Task]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        data = await self._client._get_page(_TASKS_PATH, params=raw_params)
        return [Task.model_validate(item) for item in data.get("results", [])]

    async def list_tasks_all(self, params: TaskListParams | None = None, **kwargs: Any) -> list[Task]:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_TASKS_PATH, params=raw_params)
        return [Task.model_validate(item) for item in records]

    async def list_tasks_df(self, params: TaskListParams | None = None, **kwargs: Any) -> pd.DataFrame:
        raw_params = params.model_dump(exclude_none=False) if params else {}
        raw_params.update(kwargs)
        records = await self._client._get_all_pages(_TASKS_PATH, params=raw_params)
        return self._client.to_dataframe(records)

    async def get_task(self, task_id: str) -> Task:
        """Get a single task by ID."""
        path = _TASK_DETAIL_PATH.format(task_id=task_id)
        data = await self._client._get(path)
        return Task.model_validate(data)

    async def get_timeline(self, task_id: str) -> list[TaskTimeline]:
        """Get timeline entries for a task."""
        path = _TASK_TIMELINE_PATH.format(task_id=task_id)
        data = await self._client._get(path)
        items = data if isinstance(data, list) else data.get("results", [])
        return [TaskTimeline.model_validate(item) for item in items]
