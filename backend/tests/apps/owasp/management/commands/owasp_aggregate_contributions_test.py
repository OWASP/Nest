"""Test cases for owasp_aggregate_contributions management command."""

from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.core.management import call_command

from apps.github.models import Commit, Issue, PullRequest, Release
from apps.owasp.management.commands.owasp_aggregate_contributions import Command
from apps.owasp.models import Chapter, Project


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
        return chapter

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.key = "www-project-test"
        project.name = "Test Project"
        project.owasp_repository = mock.Mock()
        project.owasp_repository.id = 1
        project.repositories.all.return_value = [mock.Mock(id=2), mock.Mock(id=3)]
        return project

    def test_aggregate_contribution_dates_helper(self, command):
        """Test the helper method that aggregates dates."""
        contribution_map = {}
        
        # Create mock queryset with dates
        mock_dates = [
            datetime(2024, 11, 16, 10, 0, 0),
            datetime(2024, 11, 16, 14, 0, 0),  # Same day
            datetime(2024, 11, 17, 9, 0, 0),
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
        start_date = datetime.now() - timedelta(days=365)
        
        # Mock querysets
        mock_commit.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 10, 0, 0),
        ]
        mock_issue.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 11, 0, 0),
        ]
        mock_pr.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 10, 0, 0),
        ]
        mock_release.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 12, 0, 0),
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
        start_date = datetime.now() - timedelta(days=365)
        
        # Mock querysets
        mock_commit.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 16, 10, 0, 0),
            datetime(2024, 11, 16, 14, 0, 0),
        ]
        mock_issue.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 17, 11, 0, 0),
        ]
        mock_pr.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 18, 10, 0, 0),
        ]
        mock_release.objects.filter.return_value.values_list.return_value = [
            datetime(2024, 11, 18, 12, 0, 0),
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
        start_date = datetime.now() - timedelta(days=365)
        
        result = command.aggregate_chapter_contributions(mock_chapter, start_date)
        
        assert result == {}

    def test_aggregate_project_without_repositories(self, command, mock_project):
        """Test that projects without repositories return empty map."""
        mock_project.owasp_repository = None
        mock_project.repositories.all.return_value = []
        start_date = datetime.now() - timedelta(days=365)
        
        result = command.aggregate_project_contributions(mock_project, start_date)
        
        assert result == {}

    @mock.patch.object(Chapter, "bulk_save")
    @mock.patch.object(Chapter.objects, "filter")
    def test_handle_chapters_only(self, mock_filter, mock_bulk_save, command, mock_chapter):
        """Test command execution for chapters only."""
        mock_filter.return_value = [mock_chapter]
        
        with mock.patch.object(
            command,
            "aggregate_chapter_contributions",
            return_value={"2024-11-16": 5},
        ):
            command.handle(entity_type="chapter", days=365)
        
        assert mock_chapter.contribution_data == {"2024-11-16": 5}
        assert mock_bulk_save.called

    @mock.patch.object(Project, "bulk_save")
    @mock.patch.object(Project.objects, "filter")
    def test_handle_projects_only(self, mock_filter, mock_bulk_save, command, mock_project):
        """Test command execution for projects only."""
        mock_filter.return_value = [mock_project]
        
        with mock.patch.object(
            command,
            "aggregate_project_contributions",
            return_value={"2024-11-16": 10},
        ):
            command.handle(entity_type="project", days=365)
        
        assert mock_project.contribution_data == {"2024-11-16": 10}
        assert mock_bulk_save.called

    @mock.patch.object(Chapter, "bulk_save")
    @mock.patch.object(Project, "bulk_save")
    @mock.patch.object(Chapter.objects, "filter")
    @mock.patch.object(Project.objects, "filter")
    def test_handle_both_entities(
        self,
        mock_project_filter,
        mock_chapter_filter,
        mock_project_bulk_save,
        mock_chapter_bulk_save,
        command,
        mock_chapter,
        mock_project,
    ):
        """Test command execution for both chapters and projects."""
        mock_chapter_filter.return_value = [mock_chapter]
        mock_project_filter.return_value = [mock_project]
        
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
            command.handle(entity_type="both", days=365)
        
        assert mock_chapter_bulk_save.called
        assert mock_project_bulk_save.called

    @mock.patch.object(Chapter.objects, "filter")
    def test_handle_with_specific_key(self, mock_filter, command, mock_chapter):
        """Test command execution with a specific entity key."""
        mock_filter.return_value = [mock_chapter]
        
        with (
            mock.patch.object(Chapter, "bulk_save"),
            mock.patch.object(
                command,
                "aggregate_chapter_contributions",
                return_value={"2024-11-16": 3},
            ),
        ):
            command.handle(entity_type="chapter", key="www-chapter-test", days=365)
        
        # Verify filter was called with the specific key
        mock_filter.assert_called()

    @mock.patch.object(Chapter.objects, "filter")
    def test_handle_with_offset(self, mock_filter, command, mock_chapter):
        """Test command execution with offset parameter."""
        chapters = [mock_chapter, mock_chapter, mock_chapter]
        mock_queryset = mock.Mock()
        mock_queryset.__getitem__.return_value = chapters[2:]  # Skip first 2
        mock_filter.return_value = mock_queryset
        
        with (
            mock.patch.object(Chapter, "bulk_save"),
            mock.patch.object(
                command,
                "aggregate_chapter_contributions",
                return_value={"2024-11-16": 1},
            ),
        ):
            command.handle(entity_type="chapter", offset=2, days=365)
        
        # Verify offset was applied
        mock_queryset.__getitem__.assert_called_with(slice(2, None))

    def test_handle_custom_days(self, command, mock_chapter):
        """Test command execution with custom days parameter."""
        with (
            mock.patch.object(Chapter.objects, "filter", return_value=[mock_chapter]),
            mock.patch.object(Chapter, "bulk_save"),
            mock.patch.object(
                command,
                "aggregate_chapter_contributions",
                return_value={},
            ) as mock_aggregate,
        ):
            command.handle(entity_type="chapter", days=90)
        
        # Verify aggregate was called with correct start_date
        assert mock_aggregate.called
        call_args = mock_aggregate.call_args[0]
        start_date = call_args[1]
        expected_start = datetime.now() - timedelta(days=90)
        
        # Allow 1 second tolerance for test execution time
        assert abs((expected_start - start_date).total_seconds()) < 1
