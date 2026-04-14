"""Tests for the tasks resource."""

from __future__ import annotations

import httpx
import pytest

from assured.models.tasks import TaskCreate
from tests.conftest import paginated_response

_EXPIRABLES_URL = "https://test-api.example.com/api/v1/task-management/expirables/"
_TASKS_URL = "https://test-api.example.com/api/v1/task-management/tasks/"
_TASK_DETAIL_URL = "https://test-api.example.com/api/v1/task-management/tasks/task-1/"


@pytest.mark.asyncio
async def test_list_expirables(client, mock_api):
    mock_api.get(_EXPIRABLES_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "exp-1", "name": "License Renewal", "archived": False},
                ]
            ),
        )
    )

    tasks = await client.tasks.list_expirables()
    assert len(tasks) == 1
    assert tasks[0].name == "License Renewal"


@pytest.mark.asyncio
async def test_list_tasks(client, mock_api):
    mock_api.get(_TASKS_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "task-1", "name": "Follow up", "status": "OPEN"},
                ]
            ),
        )
    )

    tasks = await client.tasks.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].status == "OPEN"


@pytest.mark.asyncio
async def test_create_task(client, mock_api):
    mock_api.post(_TASKS_URL).mock(
        return_value=httpx.Response(
            201,
            json={"id": "new-task", "name": "New Task", "status": "OPEN"},
        )
    )

    result = await client.tasks.create_task(TaskCreate(name="New Task"))
    assert result["id"] == "new-task"


@pytest.mark.asyncio
async def test_get_task(client, mock_api):
    mock_api.get(_TASK_DETAIL_URL).mock(
        return_value=httpx.Response(
            200,
            json={"id": "task-1", "name": "Follow up", "status": "OPEN"},
        )
    )

    task = await client.tasks.get_task("task-1")
    assert task.id == "task-1"


@pytest.mark.asyncio
async def test_list_expirables_df(client, mock_api):
    mock_api.get(_EXPIRABLES_URL).mock(
        return_value=httpx.Response(
            200,
            json=paginated_response(
                [
                    {"id": "exp-1", "name": "License Renewal"},
                ]
            ),
        )
    )

    df = await client.tasks.list_expirables_df()
    assert len(df) == 1
    assert "name" in df.columns
