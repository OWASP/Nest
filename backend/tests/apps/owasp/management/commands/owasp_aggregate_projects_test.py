from argparse import ArgumentParser
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_aggregate_projects import Command, Project


class MockQuerySet(list):
    """Helper class to simulate a QuerySet with exists() method."""

    def exists(self):
        return bool(self)


class TestOwaspAggregateProjects:
    @pytest.fixture
    def command(self):
        return Command()

    def test_add_arguments(self, command):
        """Test add_arguments adds expected arguments."""
        parser = ArgumentParser()
        command.add_arguments(parser)
        args = parser.parse_args([])
        assert args.offset == 0

    @pytest.fixture
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.owasp_url = "https://owasp.org/www-project-test"
        project.related_urls = {"https://github.com/OWASP/test-repo"}
        project.invalid_urls = set()

        project.repositories.all.return_value = []
        project.owasp_repository = mock.Mock()
        project.owasp_repository.is_archived = False
        project.owasp_repository.created_at = "2024-01-01T00:00:00Z"
        return project

    @pytest.mark.parametrize(
        ("offset", "projects"),
        [
            (0, 3),
            (2, 5),
            (0, 6),
            (1, 8),
        ],
    )
    @mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle(self, mock_bulk_save, command, mock_project, offset, projects):
        mock_organization = mock.Mock()
        mock_repository = mock.Mock()
        mock_repository.organization = mock_organization
        mock_repository.owner = mock.Mock()
        mock_repository.is_archived = False
        mock_repository.pushed_at = "2024-12-28T00:00:00Z"
        mock_repository.latest_release = mock.Mock()
        mock_repository.latest_release.published_at = "2024-12-27T00:00:00Z"
        mock_repository.commits_count = 10
        mock_repository.contributors_count = 5
        mock_repository.forks_count = 2
        mock_repository.open_issues_count = 4
        mock_repository.releases.count.return_value = 1
        mock_repository.stars_count = 50
        mock_repository.subscribers_count = 3
        mock_repository.watchers_count = 7
        mock_repository.top_languages = ["Python", "JavaScript"]
        mock_repository.license = "MIT"
        mock_repository.topics = ["security", "owasp"]

        mock_project.repositories.all.return_value = [mock_repository]
        mock_project.repositories.filter.return_value = MockQuerySet([mock_repository])
        mock_projects_list = [mock_project] * projects
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = len(mock_projects_list)
        mock_active_projects.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with mock.patch.object(Project, "active_projects", mock_active_projects):
            command.stdout = mock.MagicMock()
            command.handle(offset=offset)

        mock_bulk_save.assert_called()
        assert command.stdout.write.call_count == projects - offset

        for call in command.stdout.write.call_args_list:
            args = call[0]
            assert "https://owasp.org/www-project-test" in args[0]

    @mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle_deactivates_archived_project(self, mock_bulk_save, command, mock_project):
        """Test that project with archived repository is deactivated."""
        mock_project.owasp_repository.is_archived = True

        mock_organization = mock.Mock()
        mock_repository = mock.Mock()
        mock_repository.organization = mock_organization
        mock_repository.owner = mock.Mock()
        mock_repository.is_archived = False
        mock_repository.pushed_at = "2024-12-28T00:00:00Z"
        mock_repository.latest_release = None
        mock_repository.commits_count = 10
        mock_repository.contributors_count = 5
        mock_repository.forks_count = 2
        mock_repository.open_issues_count = 4
        mock_repository.releases.count.return_value = 0
        mock_repository.stars_count = 50
        mock_repository.subscribers_count = 3
        mock_repository.watchers_count = 7
        mock_repository.top_languages = []
        mock_repository.license = None
        mock_repository.topics = None

        mock_project.repositories.all.return_value = [mock_repository]
        mock_project.repositories.filter.return_value = MockQuerySet([mock_repository])
        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with mock.patch.object(Project, "active_projects", mock_active_projects):
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        assert not mock_project.is_active
        mock_bulk_save.assert_called()

    @mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle_no_release_or_license(self, mock_bulk_save, command, mock_project):
        """Test handle when repository has no latest_release or license."""
        mock_repository = mock.Mock()
        mock_repository.organization = None
        mock_repository.owner = mock.Mock()
        mock_repository.is_archived = False
        mock_repository.pushed_at = "2024-12-28T00:00:00Z"
        mock_repository.latest_release = None
        mock_repository.commits_count = 10
        mock_repository.contributors_count = 5
        mock_repository.forks_count = 2
        mock_repository.open_issues_count = 4
        mock_repository.releases.count.return_value = 0
        mock_repository.stars_count = 50
        mock_repository.subscribers_count = 3
        mock_repository.watchers_count = 7
        mock_repository.top_languages = []
        mock_repository.license = None
        mock_repository.topics = None
        mock_project.repositories.all.return_value = [mock_repository]
        mock_project.repositories.filter.return_value = MockQuerySet([mock_repository])
        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with mock.patch.object(Project, "active_projects", mock_active_projects):
            command.stdout = mock.MagicMock()
            command.handle(offset=0)
        mock_bulk_save.assert_called()

    @mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle_uses_max_for_stars_forks_contributors(
        self, mock_bulk_save, command, mock_project
    ):
        """Test that stars, forks, and contributors use max instead of sum."""
        mock_repo1 = mock.Mock()
        mock_repo1.organization = mock.Mock()
        mock_repo1.owner = mock.Mock()
        mock_repo1.pushed_at = "2024-12-28T00:00:00Z"
        mock_repo1.latest_release = None
        mock_repo1.commits_count = 10
        mock_repo1.contributors_count = 5
        mock_repo1.forks_count = 20
        mock_repo1.open_issues_count = 4
        mock_repo1.releases.count.return_value = 0
        mock_repo1.stars_count = 100
        mock_repo1.subscribers_count = 3
        mock_repo1.watchers_count = 7
        mock_repo1.top_languages = ["Python"]
        mock_repo1.license = "MIT"
        mock_repo1.topics = ["security"]

        mock_repo2 = mock.Mock()
        mock_repo2.organization = None
        mock_repo2.owner = mock.Mock()
        mock_repo2.pushed_at = "2024-12-29T00:00:00Z"
        mock_repo2.latest_release = None
        mock_repo2.commits_count = 20
        mock_repo2.contributors_count = 8
        mock_repo2.forks_count = 15
        mock_repo2.open_issues_count = 2
        mock_repo2.releases.count.return_value = 0
        mock_repo2.stars_count = 50
        mock_repo2.subscribers_count = 5
        mock_repo2.watchers_count = 10
        mock_repo2.top_languages = ["JavaScript"]
        mock_repo2.license = "Apache-2.0"
        mock_repo2.topics = ["owasp"]

        mock_project.repositories.filter.return_value = MockQuerySet([mock_repo1, mock_repo2])
        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.side_effect = lambda idx: (
            mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with mock.patch.object(Project, "active_projects", mock_active_projects):
            command.stdout = mock.MagicMock()
            command.handle(offset=0)

        # Stars, forks, contributors should use max, not sum.
        assert mock_project.stars_count == 100  # max(100, 50), not 150
        assert mock_project.forks_count == 20  # max(20, 15), not 35
        assert mock_project.contributors_count == 8  # max(5, 8), not 13

        # Commits should still be summed.
        assert mock_project.commits_count == 30  # 10 + 20
