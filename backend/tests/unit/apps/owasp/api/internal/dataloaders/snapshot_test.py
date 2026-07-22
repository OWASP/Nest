"""Tests for snapshot dataloaders."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from django.db.models import F
from strawberry.dataloader import DataLoader

from apps.owasp.api.internal.dataloaders.snapshot import (
    NEW_CHAPTERS_BY_SNAPSHOT_ID,
    NEW_ISSUES_BY_SNAPSHOT_ID,
    NEW_PROJECTS_BY_SNAPSHOT_ID,
    NEW_RELEASES_BY_SNAPSHOT_ID,
    NEW_USERS_BY_SNAPSHOT_ID,
    RECENT_ISSUES_LIMIT,
    get_snapshot_loaders,
    load_new_chapters_by_snapshot_id,
    load_new_issues_by_snapshot_id,
    load_new_projects_by_snapshot_id,
    load_new_releases_by_snapshot_id,
    load_new_users_by_snapshot_id,
)


class TestLoadNewChaptersBySnapshotId:
    """Tests for load_new_chapters_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Chapter")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_chapter, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, order_by."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_chapter.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_new_chapters_by_snapshot_id(snapshot_ids)

        mock_chapter.objects.filter.assert_called_once_with(snapshots__in=snapshot_ids)
        mock_filter.annotate.assert_called_once_with(snapshot_id=F("snapshots__pk"))
        mock_filter.annotate.return_value.order_by.assert_called_once_with("-created_at")

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Chapter")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_chapter, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_chapter.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_new_chapters_by_snapshot_id(snapshot_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, snapshot_ids, key_field="snapshot_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Chapter")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_chapter, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_chapter_a = MagicMock()
        mock_chapter_b = MagicMock()
        expected = [[mock_chapter_a, mock_chapter_b], [], [mock_chapter_a]]
        mock_filter = mock_chapter.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_new_chapters_by_snapshot_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Chapter")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_chapter, mock_get_results_by_keys):
        """An empty snapshot_ids list results in an empty filter and empty return."""
        mock_filter = mock_chapter.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_new_chapters_by_snapshot_id([])

        mock_chapter.objects.filter.assert_called_once_with(snapshots__in=[])
        assert result == []

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Chapter")
    @pytest.mark.asyncio
    async def test_single_snapshot_id(self, mock_chapter, mock_get_results_by_keys):
        """A single-element list is handled correctly end-to-end."""
        mock_chapter_obj = MagicMock()
        mock_filter = mock_chapter.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = [[mock_chapter_obj]]

        result = await load_new_chapters_by_snapshot_id([42])

        mock_chapter.objects.filter.assert_called_once_with(snapshots__in=[42])
        assert result == [[mock_chapter_obj]]


class TestLoadNewIssuesBySnapshotId:
    """Tests for load_new_issues_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Issue")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_issue, mock_get_results_by_keys):
        """Queryset is built with filter, annotate, annotate(row_number), filter, order_by."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_windowed = mock_filter.annotate.return_value.annotate.return_value
        mock_windowed.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_new_issues_by_snapshot_id(snapshot_ids)

        mock_issue.objects.filter.assert_called_once_with(snapshots__in=snapshot_ids)
        mock_filter.annotate.assert_called_once_with(snapshot_id=F("snapshots__pk"))
        mock_filter.annotate.return_value.annotate.assert_called_once()
        assert "row_number" in mock_filter.annotate.return_value.annotate.call_args.kwargs
        mock_windowed.filter.assert_called_once_with(row_number__lte=RECENT_ISSUES_LIMIT)
        mock_windowed.filter.return_value.order_by.assert_called_once_with(
            "snapshot_id", "-created_at"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Issue")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_issue, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_windowed = mock_filter.annotate.return_value.annotate.return_value
        mock_windowed.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_new_issues_by_snapshot_id(snapshot_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, snapshot_ids, key_field="snapshot_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Issue")
    @pytest.mark.asyncio
    async def test_window_filter_enforces_limit(self, mock_issue, mock_get_results_by_keys):
        """The window function filter enforces the RECENT_ISSUES_LIMIT."""
        mock_qs = MagicMock()
        mock_filter = mock_issue.objects.filter.return_value
        mock_windowed = mock_filter.annotate.return_value.annotate.return_value
        mock_windowed.filter.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[MagicMock() for _ in range(RECENT_ISSUES_LIMIT)]]

        result = await load_new_issues_by_snapshot_id([1])

        mock_windowed.filter.assert_called_once_with(row_number__lte=RECENT_ISSUES_LIMIT)
        assert len(result[0]) == RECENT_ISSUES_LIMIT

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Issue")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_issue, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_issue_a = MagicMock()
        mock_issue_b = MagicMock()
        expected = [[mock_issue_a, mock_issue_b], [], [mock_issue_a]]
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_new_issues_by_snapshot_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Issue")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_issue, mock_get_results_by_keys):
        """An empty snapshot_ids list results in an empty filter and empty return."""
        mock_filter = mock_issue.objects.filter.return_value
        mock_filter.annotate.return_value.filter.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_new_issues_by_snapshot_id([])

        mock_issue.objects.filter.assert_called_once_with(snapshots__in=[])
        assert result == []


class TestLoadNewProjectsBySnapshotId:
    """Tests for load_new_projects_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Project")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_project, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, order_by."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_new_projects_by_snapshot_id(snapshot_ids)

        mock_project.objects.filter.assert_called_once_with(snapshots__in=snapshot_ids)
        mock_filter.annotate.assert_called_once_with(snapshot_id=F("snapshots__pk"))
        mock_filter.annotate.return_value.order_by.assert_called_once_with("-created_at")

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Project")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_project, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_new_projects_by_snapshot_id(snapshot_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, snapshot_ids, key_field="snapshot_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Project")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_project, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_project_a = MagicMock()
        mock_project_b = MagicMock()
        expected = [[mock_project_a, mock_project_b], [], [mock_project_a]]
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_new_projects_by_snapshot_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Project")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_project, mock_get_results_by_keys):
        """An empty snapshot_ids list results in an empty filter and empty return."""
        mock_filter = mock_project.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_new_projects_by_snapshot_id([])

        mock_project.objects.filter.assert_called_once_with(snapshots__in=[])
        assert result == []


class TestLoadNewReleasesBySnapshotId:
    """Tests for load_new_releases_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Release")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(
        self, mock_release, mock_get_results_by_keys
    ):
        """Queryset is built with filter, annotate, order_by."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_new_releases_by_snapshot_id(snapshot_ids)

        mock_release.objects.filter.assert_called_once_with(snapshots__in=snapshot_ids)
        mock_filter.annotate.assert_called_once_with(snapshot_id=F("snapshots__pk"))
        mock_filter.annotate.return_value.order_by.assert_called_once_with("-published_at")

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Release")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_release, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_new_releases_by_snapshot_id(snapshot_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, snapshot_ids, key_field="snapshot_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Release")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_release, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_release_a = MagicMock()
        mock_release_b = MagicMock()
        expected = [[mock_release_a, mock_release_b], [], [mock_release_a]]
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_new_releases_by_snapshot_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.Release")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_release, mock_get_results_by_keys):
        """An empty snapshot_ids list results in an empty filter and empty return."""
        mock_filter = mock_release.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_new_releases_by_snapshot_id([])

        mock_release.objects.filter.assert_called_once_with(snapshots__in=[])
        assert result == []


class TestLoadNewUsersBySnapshotId:
    """Tests for load_new_users_by_snapshot_id."""

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.User")
    @pytest.mark.asyncio
    async def test_builds_queryset_with_correct_chain(self, mock_user, mock_get_results_by_keys):
        """Queryset is built with filter, annotate, order_by."""
        snapshot_ids = [1, 2, 3]
        mock_qs = MagicMock()
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], [], []]

        await load_new_users_by_snapshot_id(snapshot_ids)

        mock_user.objects.filter.assert_called_once_with(snapshots__in=snapshot_ids)
        mock_filter.annotate.assert_called_once_with(snapshot_id=F("snapshots__pk"))
        mock_filter.annotate.return_value.order_by.assert_called_once_with("-created_at")

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.User")
    @pytest.mark.asyncio
    async def test_delegates_to_get_results_by_keys_correct_args(
        self, mock_user, mock_get_results_by_keys
    ):
        """get_results_by_keys receives the queryset, ids, and correct key_field."""
        snapshot_ids = [10, 20]
        mock_qs = MagicMock()
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = mock_qs
        mock_get_results_by_keys.return_value = [[], []]

        await load_new_users_by_snapshot_id(snapshot_ids)

        mock_get_results_by_keys.assert_called_once_with(
            mock_qs, snapshot_ids, key_field="snapshot_id"
        )

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.User")
    @pytest.mark.asyncio
    async def test_returns_result_from_get_results_by_keys(
        self, mock_user, mock_get_results_by_keys
    ):
        """The return value is exactly what get_results_by_keys resolves to."""
        mock_user_a = MagicMock()
        mock_user_b = MagicMock()
        expected = [[mock_user_a, mock_user_b], [], [mock_user_a]]
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = expected

        result = await load_new_users_by_snapshot_id([1, 2, 3])

        assert result is expected

    @patch(
        "apps.owasp.api.internal.dataloaders.snapshot.get_results_by_keys",
        new_callable=AsyncMock,
    )
    @patch("apps.owasp.api.internal.dataloaders.snapshot.User")
    @pytest.mark.asyncio
    async def test_empty_snapshot_ids(self, mock_user, mock_get_results_by_keys):
        """An empty snapshot_ids list results in an empty filter and empty return."""
        mock_filter = mock_user.objects.filter.return_value
        mock_filter.annotate.return_value.order_by.return_value = MagicMock()
        mock_get_results_by_keys.return_value = []

        result = await load_new_users_by_snapshot_id([])

        mock_user.objects.filter.assert_called_once_with(snapshots__in=[])
        assert result == []


class TestGetSnapshotLoaders:
    """Tests for get_snapshot_loaders."""

    @pytest.mark.parametrize(
        "loader_key",
        [
            NEW_CHAPTERS_BY_SNAPSHOT_ID,
            NEW_ISSUES_BY_SNAPSHOT_ID,
            NEW_PROJECTS_BY_SNAPSHOT_ID,
            NEW_RELEASES_BY_SNAPSHOT_ID,
            NEW_USERS_BY_SNAPSHOT_ID,
        ],
    )
    def test_returns_mapping(self, loader_key):
        """Factory always returns a Mapping."""
        loaders = get_snapshot_loaders()
        assert loader_key in loaders
        assert isinstance(loaders[loader_key], DataLoader)

    def test_load_fn_is_load_new_chapters_by_snapshot_id(self):
        """The new_chapters loader is wired to load_new_chapters_by_snapshot_id."""
        loaders = get_snapshot_loaders()
        assert loaders[NEW_CHAPTERS_BY_SNAPSHOT_ID].load_fn is load_new_chapters_by_snapshot_id

    def test_load_fn_is_load_new_issues_by_snapshot_id(self):
        """The new_issues loader is wired to load_new_issues_by_snapshot_id."""
        loaders = get_snapshot_loaders()
        assert loaders[NEW_ISSUES_BY_SNAPSHOT_ID].load_fn is load_new_issues_by_snapshot_id

    def test_load_fn_is_load_new_projects_by_snapshot_id(self):
        """The new_projects loader is wired to load_new_projects_by_snapshot_id."""
        loaders = get_snapshot_loaders()
        assert loaders[NEW_PROJECTS_BY_SNAPSHOT_ID].load_fn is load_new_projects_by_snapshot_id

    def test_load_fn_is_load_new_releases_by_snapshot_id(self):
        """The new_releases loader is wired to load_new_releases_by_snapshot_id."""
        loaders = get_snapshot_loaders()
        assert loaders[NEW_RELEASES_BY_SNAPSHOT_ID].load_fn is load_new_releases_by_snapshot_id

    def test_load_fn_is_load_new_users_by_snapshot_id(self):
        """The new_users loader is wired to load_new_users_by_snapshot_id."""
        loaders = get_snapshot_loaders()
        assert loaders[NEW_USERS_BY_SNAPSHOT_ID].load_fn is load_new_users_by_snapshot_id

    @pytest.mark.parametrize(
        "loader_key",
        [
            NEW_CHAPTERS_BY_SNAPSHOT_ID,
            NEW_ISSUES_BY_SNAPSHOT_ID,
            NEW_PROJECTS_BY_SNAPSHOT_ID,
            NEW_RELEASES_BY_SNAPSHOT_ID,
            NEW_USERS_BY_SNAPSHOT_ID,
        ],
    )
    def test_returns_new_instances_on_each_call(self, loader_key):
        """Each call produces distinct DataLoader instances for per-request isolation."""
        loaders1 = get_snapshot_loaders()
        loaders2 = get_snapshot_loaders()
        assert loaders1 is not loaders2
        assert loaders1[loader_key] is not loaders2[loader_key]
