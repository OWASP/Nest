"""Tests for member snapshot dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.member_snapshot import (
    COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
    ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
    MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
    PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
    TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
    get_member_snapshot_loaders,
    load_commits_count_by_snapshot_id,
    load_count_by_snapshot_id,
    load_issues_count_by_snapshot_id,
    load_messages_count_by_snapshot_id,
    load_pull_requests_count_by_snapshot_id,
    load_total_contributions_by_snapshot_id,
)


class TestLoadCountBySnapshotId:
    """Tests for load_count_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_snapshot, mock_get_values_by_keys):
        """Queryset is built with filter, annotate, and values_list."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = [0, 0, 0]

        await load_count_by_snapshot_id(snapshot_ids, "commits")

        mock_snapshot.objects.filter.assert_called_once_with(pk__in=snapshot_ids)
        mock_filter.annotate.assert_called_once()
        mock_filter.annotate.return_value.values_list.assert_called_once_with("pk", "count")

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_delegates_to_get_values_by_keys(self, mock_snapshot, mock_get_values_by_keys):
        """get_values_by_keys receives the queryset, ids, and default=0."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = [0, 0]

        await load_count_by_snapshot_id(snapshot_ids, "issues")

        mock_get_values_by_keys.assert_called_once_with(mock_qs, snapshot_ids, default=0)

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_values_by_keys(
        self, mock_snapshot, mock_get_values_by_keys
    ):
        """The return value is what get_values_by_keys resolves to."""
        snapshot_ids = [1, 2]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        expected = [5, 7]
        mock_get_values_by_keys.return_value = expected

        result = await load_count_by_snapshot_id(snapshot_ids, "commits")

        assert result == expected

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_snapshot, mock_get_values_by_keys):
        """An empty snapshot_ids list delegates to get_values_by_keys and returns its result."""
        snapshot_ids = []
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = []

        result = await load_count_by_snapshot_id(snapshot_ids, "commits")

        assert result == []


class TestLoadCommitsCountBySnapshotId:
    """Tests for load_commits_count_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.load_count_by_snapshot_id",
        new_callable=AsyncMock,
    )
    @pytest.mark.asyncio
    async def test_delegates_to_load_count_with_commits_field(self, mock_load_count):
        """Delegates to load_count_by_snapshot_id with the 'commits' field."""
        snapshot_ids = [1, 2]
        expected = [5, 10]
        mock_load_count.return_value = expected

        result = await load_commits_count_by_snapshot_id(snapshot_ids)

        mock_load_count.assert_awaited_once_with(snapshot_ids, "commits")
        assert result == expected


class TestLoadIssuesCountBySnapshotId:
    """Tests for load_issues_count_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.load_count_by_snapshot_id",
        new_callable=AsyncMock,
    )
    @pytest.mark.asyncio
    async def test_delegates_to_load_count_with_issues_field(self, mock_load_count):
        """Delegates to load_count_by_snapshot_id with the 'issues' field."""
        snapshot_ids = [1, 2]
        expected = [3, 4]
        mock_load_count.return_value = expected

        result = await load_issues_count_by_snapshot_id(snapshot_ids)

        mock_load_count.assert_awaited_once_with(snapshot_ids, "issues")
        assert result == expected


class TestLoadMessagesCountBySnapshotId:
    """Tests for load_messages_count_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.load_count_by_snapshot_id",
        new_callable=AsyncMock,
    )
    @pytest.mark.asyncio
    async def test_delegates_to_load_count_with_messages_field(self, mock_load_count):
        """Delegates to load_count_by_snapshot_id with the 'messages' field."""
        snapshot_ids = [1, 2]
        expected = [100, 200]
        mock_load_count.return_value = expected

        result = await load_messages_count_by_snapshot_id(snapshot_ids)

        mock_load_count.assert_awaited_once_with(snapshot_ids, "messages")
        assert result == expected


class TestLoadPullRequestsCountBySnapshotId:
    """Tests for load_pull_requests_count_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.load_count_by_snapshot_id",
        new_callable=AsyncMock,
    )
    @pytest.mark.asyncio
    async def test_delegates_to_load_count_with_pull_requests_field(self, mock_load_count):
        """Delegates to load_count_by_snapshot_id with the 'pull_requests' field."""
        snapshot_ids = [1, 2]
        expected = [23, 45]
        mock_load_count.return_value = expected

        result = await load_pull_requests_count_by_snapshot_id(snapshot_ids)

        mock_load_count.assert_awaited_once_with(snapshot_ids, "pull_requests")
        assert result == expected


class TestLoadTotalContributionsBySnapshotId:
    """Tests for load_total_contributions_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_snapshot, mock_get_values_by_keys):
        """Outer queryset filters by pk__in, annotates total, and uses values_list."""
        snapshot_ids = [1, 2]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = [0, 0]

        await load_total_contributions_by_snapshot_id(snapshot_ids)

        mock_snapshot.objects.filter.assert_any_call(pk__in=snapshot_ids)
        mock_filter.annotate.return_value.values_list.assert_called_once_with("pk", "total")

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_delegates_to_get_values_by_keys(self, mock_snapshot, mock_get_values_by_keys):
        """get_values_by_keys receives the queryset, ids, and default=0."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = [0, 0]

        await load_total_contributions_by_snapshot_id(snapshot_ids)

        mock_get_values_by_keys.assert_called_once_with(mock_qs, snapshot_ids, default=0)

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_values_by_keys(
        self, mock_snapshot, mock_get_values_by_keys
    ):
        """The return value is what get_values_by_keys resolves to."""
        snapshot_ids = [1, 2]
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        expected = [80, 120]
        mock_get_values_by_keys.return_value = expected

        result = await load_total_contributions_by_snapshot_id(snapshot_ids)

        assert result == expected

    @patch(
        "apps.owasp.api.internal.dataloaders.member_snapshot.get_values_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.member_snapshot.MemberSnapshot")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_snapshot, mock_get_values_by_keys):
        """An empty snapshot_ids list delegates to get_values_by_keys and returns its result."""
        snapshot_ids = []
        mock_qs = MagicMock()
        mock_filter = mock_snapshot.objects.filter.return_value
        mock_filter.annotate.return_value.values_list.return_value = mock_qs
        mock_get_values_by_keys.return_value = []

        result = await load_total_contributions_by_snapshot_id(snapshot_ids)

        assert result == []


class TestGetMemberSnapshotLoaders:
    """Tests for get_member_snapshot_loaders."""

    def test_returns_mapping_with_all_loaders(self):
        """Factory returns a mapping with all loaders."""
        loaders = get_member_snapshot_loaders()
        assert COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER in loaders
        assert ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER in loaders
        assert MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER in loaders
        assert PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER in loaders
        assert TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER in loaders
        assert isinstance(loaders[COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER], DataLoader)
        assert isinstance(loaders[ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER], DataLoader)
        assert isinstance(loaders[MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER], DataLoader)
        assert isinstance(loaders[PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER], DataLoader)
        assert isinstance(loaders[TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER], DataLoader)

    def test_returns_new_instances_on_each_call(self):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_member_snapshot_loaders()
        loaders2 = get_member_snapshot_loaders()
        assert loaders1 is not loaders2
        for key in (
            COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER,
            ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER,
            MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER,
            PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER,
            TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER,
        ):
            assert loaders1[key] is not loaders2[key]

    def test_load_fn_is_correct(self):
        """Each loader is wired to its correct load function."""
        loaders = get_member_snapshot_loaders()
        assert (
            loaders[COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER].load_fn
            is load_commits_count_by_snapshot_id
        )
        assert (
            loaders[ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER].load_fn is load_issues_count_by_snapshot_id
        )
        assert (
            loaders[MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER].load_fn
            is load_messages_count_by_snapshot_id
        )
        assert (
            loaders[PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER].load_fn
            is load_pull_requests_count_by_snapshot_id
        )
        assert (
            loaders[TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER].load_fn
            is load_total_contributions_by_snapshot_id
        )
