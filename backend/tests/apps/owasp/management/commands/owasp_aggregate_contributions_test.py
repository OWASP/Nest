"""Test cases for owasp_aggregate_contributions management command."""

from datetime import UTC, datetime, timedelta
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_aggregate_contributions import Command
from apps.owasp.models import Chapter, Project


class MockQuerySet:
    """Mock QuerySet that supports slicing and iteration without database access."""

    def __init__(self, items):
        self._items = items

    def __iter__(self):
        """Return iterator over items."""
        return iter(self._items)

    def __getitem__(self, key):
        """Get item by key or slice."""
        if isinstance(key, slice):
            return MockQuerySet(self._items[key])
        return self._items[key]

    def filter(self, **kwargs):
        # Return self to support filter chaining
        return self

    def order_by(self, *_fields):
        """Mock order_by method."""
        return self

    def select_related(self, *_):
        """Mock select_related method."""
        return self

    def prefetch_related(self, *_):
        """Mock prefetch_related method."""
        return self

    def __len__(self):
        """Return length of items."""
        return len(self._items)


class TestOwaspAggregateContributions:
    @pytest.fixture
    def command(self):
        return Command()

    @pytest.fixture
    def mock_chapter(self):
        chapter = mock.Mock(spec=Chapter)
        chapter.key = "www-chapter-test"
        chapter.name = "Test Chapter"
        chapter.owasp_repository = mock.Mock()
        chapter.owasp_repository.id = 1
        # Fix Django ORM compatibility
        chapter.owasp_repository.resolve_expression = mock.Mock(
            return_value=chapter.owasp_repository
        )
        chapter.owasp_repository.get_source_expressions = mock.Mock(return_value=[])
        return chapter

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.key = "www-project-test"
        project.name = "Test Project"
        project.owasp_repository = mock.Mock()
        project.owasp_repository.id = 1
        # Fix Django ORM compatibility
        project.owasp_repository.resolve_expression = mock.Mock(
            return_value=project.owasp_repository
        )
        project.owasp_repository.get_source_expressions = mock.Mock(return_value=[])

        # Mock additional repositories
        additional_repo1 = mock.Mock(id=2)
        additional_repo1.resolve_expression = mock.Mock(return_value=additional_repo1)
        additional_repo1.get_source_expressions = mock.Mock(return_value=[])

        additional_repo2 = mock.Mock(id=3)
        additional_repo2.resolve_expression = mock.Mock(return_value=additional_repo2)
        additional_repo2.get_source_expressions = mock.Mock(return_value=[])

        project.repositories.all.return_value = [additional_repo1, additional_repo2]
        return project

    def test_aggregate_contribution_dates_helper(self, command):
        """Test the helper method that aggregates dates."""
        contribution_map = {}

        # Create mock queryset with dates
        mock_dates = [
            datetime(2024, 11, 16, 10, 0, 0, tzinfo=UTC),
            datetime(2024, 11, 16, 14, 0, 0, tzinfo=UTC),  # Same day
            datetime(2024, 11, 17, 9, 0, 0, tzinfo=UTC),
            None,  # Should be skipped
        ]

        mock_queryset = mock.Mock()
        mock_queryset.values_list.return_value = mock_dates

        command._aggregate_contribution_dates(
            mock_queryset,
            "created_at",
            contribution_map,
        )

        assert contribution_map == {
            "2024-11-16": 2,
            "2024-11-17": 1,
        }

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_aggregate_chapter_contributions(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        command,
        mock_chapter,
    ):
        """Test aggregating contributions for a chapter."""
        start_date = datetime.now(tz=UTC) - timedelta(days=365)

        # Mock querysets
        mock_commit.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 10, 0, 0, tzinfo=UTC),
        ]
        mock_issue.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 11, 0, 0, tzinfo=UTC),
        ]
        mock_pr.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 10, 0, 0, tzinfo=UTC),
        ]
        mock_release.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 12, 0, 0, tzinfo=UTC),
        ]

        result = command.aggregate_chapter_contributions(mock_chapter, start_date)

        assert result == {
            "2024-11-16": 2,  # 1 commit + 1 issue
            "2024-11-17": 2,  # 1 PR + 1 release
        }

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_aggregate_project_contributions(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        command,
        mock_project,
    ):
        """Test aggregating contributions for a project."""
        start_date = datetime.now(tz=UTC) - timedelta(days=365)

        # Mock querysets
        mock_commit.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 10, 0, 0, tzinfo=UTC),
            datetime(2024, 11, 16, 14, 0, 0, tzinfo=UTC),
        ]
        mock_issue.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 11, 0, 0, tzinfo=UTC),
        ]
        mock_pr.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 18, 10, 0, 0, tzinfo=UTC),
        ]
        mock_release.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 18, 12, 0, 0, tzinfo=UTC),
        ]

        result = command.aggregate_project_contributions(mock_project, start_date)

        assert result == {
            "2024-11-16": 2,  # 2 commits
            "2024-11-17": 1,  # 1 issue
            "2024-11-18": 2,  # 1 PR + 1 release
        }

    def test_aggregate_chapter_without_repository(self, command, mock_chapter):
        """Test that chapters without repositories return empty map."""
        mock_chapter.owasp_repository = None
        start_date = datetime.now(tz=UTC) - timedelta(days=365)

        result = command.aggregate_chapter_contributions(mock_chapter, start_date)

        assert result == {}

    def test_aggregate_project_without_repositories(self, command, mock_project):
        """Test that projects without repositories return empty map."""
        mock_project.owasp_repository = None
        mock_project.repositories.all.return_value = []
        start_date = datetime.now(tz=UTC) - timedelta(days=365)

        result = command.aggregate_project_contributions(mock_project, start_date)

        assert result == {}

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Chapter")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_chapters_only(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_chapter_model,
        command,
        mock_chapter,
    ):
        """Test command execution for chapters only."""
        mock_chapter_model.objects.filter.return_value = MockQuerySet([mock_chapter])
        mock_chapter_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 5
        mock_issue.objects.filter.return_value.count.return_value = 3
        mock_pr.objects.filter.return_value.count.return_value = 2
        mock_release.objects.filter.return_value.count.return_value = 1

        with mock.patch.object(
            command,
            "aggregate_chapter_contributions",
            return_value={"2024-11-16": 5},
        ):
            command.handle(entity_type="chapter", days=365, offset=0)

        assert mock_chapter.contribution_data == {"2024-11-16": 5}
        assert mock_chapter_model.bulk_save.called

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Project")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_projects_only(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_project_model,
        command,
        mock_project,
    ):
        """Test command execution for projects only."""
        mock_project_model.objects.filter.return_value = MockQuerySet([mock_project])
        mock_project_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 8
        mock_issue.objects.filter.return_value.count.return_value = 4
        mock_pr.objects.filter.return_value.count.return_value = 3
        mock_release.objects.filter.return_value.count.return_value = 2

        with mock.patch.object(
            command,
            "aggregate_project_contributions",
            return_value={"2024-11-16": 10},
        ):
            command.handle(entity_type="project", days=365, offset=0)

        assert mock_project.contribution_data == {"2024-11-16": 10}
        assert mock_project_model.bulk_save.called

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Chapter")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Project")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_both_entities(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_project_model,
        mock_chapter_model,
        command,
        mock_chapter,
        mock_project,
    ):
        """Test command execution for both chapters and projects."""
        mock_chapter_model.objects.filter.return_value = MockQuerySet([mock_chapter])
        mock_project_model.objects.filter.return_value = MockQuerySet([mock_project])
        mock_chapter_model.bulk_save = mock.Mock()
        mock_project_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 5
        mock_issue.objects.filter.return_value.count.return_value = 3
        mock_pr.objects.filter.return_value.count.return_value = 2
        mock_release.objects.filter.return_value.count.return_value = 1

        with (
            mock.patch.object(
                command,
                "aggregate_chapter_contributions",
                return_value={"2024-11-16": 5},
            ),
            mock.patch.object(
                command,
                "aggregate_project_contributions",
                return_value={"2024-11-16": 10},
            ),
        ):
            command.handle(entity_type="both", days=365, offset=0)

        assert mock_chapter_model.bulk_save.called
        assert mock_project_model.bulk_save.called

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Chapter")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_with_specific_key(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_chapter_model,
        command,
        mock_chapter,
    ):
        """Test command execution with a specific entity key."""
        mock_chapter_model.objects.filter.return_value = MockQuerySet([mock_chapter])
        mock_chapter_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 3
        mock_issue.objects.filter.return_value.count.return_value = 2
        mock_pr.objects.filter.return_value.count.return_value = 1
        mock_release.objects.filter.return_value.count.return_value = 1

        with mock.patch.object(
            command,
            "aggregate_chapter_contributions",
            return_value={"2024-11-16": 3},
        ):
            command.handle(entity_type="chapter", key="www-chapter-test", days=365, offset=0)

        # Verify filter was called with the specific key
        mock_chapter_model.objects.filter.assert_called()

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Chapter")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_with_offset(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_chapter_model,
        command,
        mock_chapter,
    ):
        """Test command execution with offset parameter."""
        chapters = [mock_chapter, mock_chapter, mock_chapter]
        mock_chapter_model.objects.filter.return_value = MockQuerySet(chapters)
        mock_chapter_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 1
        mock_issue.objects.filter.return_value.count.return_value = 1
        mock_pr.objects.filter.return_value.count.return_value = 1
        mock_release.objects.filter.return_value.count.return_value = 0

        with mock.patch.object(
            command,
            "aggregate_chapter_contributions",
            return_value={"2024-11-16": 1},
        ) as mock_aggregate:
            command.handle(entity_type="chapter", offset=2, days=365)

        # Verify that offset was applied - only 1 chapter should be processed (3 total - 2 offset)
        mock_aggregate.assert_called_once()
        mock_chapter_model.bulk_save.assert_called_once()

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Chapter")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Commit")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Issue")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.PullRequest")
    @mock.patch("apps.owasp.management.commands.owasp_aggregate_contributions.Release")
    def test_handle_custom_days(
        self,
        mock_release,
        mock_pr,
        mock_issue,
        mock_commit,
        mock_chapter_model,
        command,
        mock_chapter,
    ):
        """Test command execution with custom days parameter."""
        mock_chapter_model.objects.filter.return_value = MockQuerySet([mock_chapter])
        mock_chapter_model.bulk_save = mock.Mock()

        # Mock ORM queries to return counts
        mock_commit.objects.filter.return_value.count.return_value = 0
        mock_issue.objects.filter.return_value.count.return_value = 0
        mock_pr.objects.filter.return_value.count.return_value = 0
        mock_release.objects.filter.return_value.count.return_value = 0

        with mock.patch.object(
            command,
            "aggregate_chapter_contributions",
            return_value={},
        ) as mock_aggregate:
            command.handle(entity_type="chapter", days=90, offset=0)

        # Verify aggregate was called with correct start_date
        assert mock_aggregate.called
        call_args = mock_aggregate.call_args[0]
        start_date = call_args[1]
        expected_start = datetime.now(tz=UTC) - timedelta(days=90)

        # Allow 1 second tolerance for test execution time
        assert abs((expected_start - start_date).total_seconds()) < 1
