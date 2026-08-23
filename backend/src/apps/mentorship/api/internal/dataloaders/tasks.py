"""Dataloaders for tasks."""

from datetime import datetime

from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys
from apps.mentorship.models.task import Task

TASK_DEADLINES_BY_ISSUE_ID_LOADER = "task_deadlines_by_issue_id"


async def load_task_deadlines_by_issue_id(issue_ids: list[int]) -> list[datetime | None]:
    """Batch-load the latest task deadlines for the given issue IDs in a single query."""
    tasks = (
        Task.objects.filter(issue_id__in=issue_ids, deadline_at__isnull=False)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("issue_id")],
                order_by=F("assigned_at").desc(),
            )
        )
        .filter(row_number=1)
    )
    return await get_result_by_keys(
        tasks, issue_ids, key_field="issue_id", value_field="deadline_at"
    )


def get_task_loaders() -> dict[str, DataLoader[int, datetime | None]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        TASK_DEADLINES_BY_ISSUE_ID_LOADER: DataLoader[int, datetime | None](
            load_fn=load_task_deadlines_by_issue_id,
        ),
    }
