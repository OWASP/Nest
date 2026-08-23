"""Tests for the task deadlines dataloader."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.mentorship.api.internal.dataloaders.tasks import (
    TASK_DEADLINES_BY_ISSUE_ID_LOADER,
    get_task_loaders,
    load_task_deadlines_by_issue_id,
)


class TestLoadTaskDeadlinesByIssueId:
    """Tests for load_task_deadlines_by_issue_id."""

    @patch(
        "apps.mentorship.api.internal.dataloaders.tasks.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.tasks.Task")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_task, mock_get_result):
        """Queryset is built with filter, annotate, and filter(row_number=1)."""
        issue_ids = [1, 2]
        mock_get_result.return_value = [None, None]

        await load_task_deadlines_by_issue_id(issue_ids)

        mock_task.objects.filter.assert_called_once_with(
            issue_id__in=issue_ids, deadline_at__isnull=False
        )
        mock_task.objects.filter.return_value.annotate.assert_called_once()
        mock_task.objects.filter.return_value.annotate.return_value.filter.assert_called_once_with(
            row_number=1
        )

    @patch(
        "apps.mentorship.api.internal.dataloaders.tasks.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.tasks.Task")
    @pytest.mark.asyncio
    async def test_delegates_to_get_result_by_keys_correct_args(self, mock_task, mock_get_result):
        """get_result_by_keys receives the queryset, issue_ids, and correct field names."""
        issue_ids = [10, 20]
        mock_get_result.return_value = [None, None]

        await load_task_deadlines_by_issue_id(issue_ids)

        mock_get_result.assert_called_once_with(
            mock_task.objects.filter.return_value.annotate.return_value.filter.return_value,
            issue_ids,
            key_field="issue_id",
            value_field="deadline_at",
        )

    @patch(
        "apps.mentorship.api.internal.dataloaders.tasks.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.tasks.Task")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_result_by_keys(self, mock_task, mock_get_result):
        """The return value is exactly what get_result_by_keys resolves to."""
        deadline = datetime(2025, 10, 26, tzinfo=UTC)
        expected = [deadline, None]
        mock_get_result.return_value = expected

        result = await load_task_deadlines_by_issue_id([1, 2])

        assert result is expected

    @patch(
        "apps.mentorship.api.internal.dataloaders.tasks.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.tasks.Task")
    @pytest.mark.asyncio
    async def test_missing_issue_resolves_to_none(self, mock_task, mock_get_result):
        """An issue ID with no deadline resolves to None."""
        mock_get_result.return_value = [None]

        result = await load_task_deadlines_by_issue_id([99])

        assert result == [None]

    @patch(
        "apps.mentorship.api.internal.dataloaders.tasks.get_result_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.mentorship.api.internal.dataloaders.tasks.Task")
    @pytest.mark.asyncio
    async def test_preserves_issue_ids_order(self, mock_task, mock_get_result):
        """The issue_ids list is forwarded to get_result_by_keys unchanged, preserving order."""
        issue_ids = [30, 10, 20]
        mock_get_result.return_value = [None, None, None]

        await load_task_deadlines_by_issue_id(issue_ids)

        _, positional_args, _ = mock_get_result.mock_calls[0]
        assert positional_args[1] is issue_ids


class TestGetTaskLoaders:
    """Tests for get_task_loaders."""

    def test_returns_mapping(self):
        """Factory always returns a Mapping."""
        loaders = get_task_loaders()
        assert TASK_DEADLINES_BY_ISSUE_ID_LOADER in loaders
        assert isinstance(loaders[TASK_DEADLINES_BY_ISSUE_ID_LOADER], DataLoader)

    def test_load_fn_is_load_task_deadlines_by_issue_id(self):
        """The by-issue-id DataLoader is wired to load_task_deadlines_by_issue_id."""
        loaders = get_task_loaders()
        loader = loaders[TASK_DEADLINES_BY_ISSUE_ID_LOADER]
        assert loader.load_fn is load_task_deadlines_by_issue_id

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_task_loaders()
        loaders2 = get_task_loaders()
        assert loaders1 is not loaders2
        assert (
            loaders1[TASK_DEADLINES_BY_ISSUE_ID_LOADER]
            is not loaders2[TASK_DEADLINES_BY_ISSUE_ID_LOADER]
        )
