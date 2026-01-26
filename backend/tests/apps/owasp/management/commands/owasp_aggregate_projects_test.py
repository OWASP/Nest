from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_aggregate_projects import Command, Project


class TestOwaspAggregateProjects:
    @pytest.fixture
    def command(self):
        return Command()

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

        class QS(list):
            def exists(self):
                return bool(self)

        mock_project.repositories.filter.return_value = QS([mock_repository])
        mock_projects_list = [mock_project] * projects
        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.count.return_value = len(mock_projects_list)
        mock_active_projects.__getitem__.side_effect = (
            lambda idx: mock_projects_list[idx.start : idx.stop]
            if isinstance(idx, slice)
            else mock_projects_list[idx]
        )
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print") as mock_print,
        ):
            command.handle(offset=offset)

        assert mock_bulk_save.called
        assert mock_print.call_count == projects - offset

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-project-test" in args[0]

    @mock.patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"})
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle_populates_pull_requests(
        self,
        mock_bulk_save,
        command,
        mock_project,
    ):
        """Check that the aggregate command copies pull requests to project.pull_requests.

        This is important because we no longer use the old
        @property-based query and rely on the M2M field instead.
        """
        mock_pr1 = mock.Mock()
        mock_pr2 = mock.Mock()

        mock_repository = mock.Mock()
        mock_repository.organization = None
        mock_repository.owner = mock.Mock()
        mock_repository.is_archived = False
        mock_repository.pushed_at = "2024-12-28T00:00:00Z"
        mock_repository.latest_release = None

        mock_repository.commits_count = 1
        mock_repository.contributors_count = 1
        mock_repository.forks_count = 1
        mock_repository.open_issues_count = 1
        mock_repository.releases.count.return_value = 0
        mock_repository.stars_count = 1
        mock_repository.subscribers_count = 1
        mock_repository.watchers_count = 1

        mock_repository.top_languages = []
        mock_repository.license = None
        mock_repository.topics = []

        mock_repository.pull_requests.all.return_value = [
            mock_pr1,
            mock_pr2,
        ]

        class QS(list):
            """Small helper to mock queryset behavior."""

            def exists(self):
                return bool(self)

        mock_project.repositories.all.return_value = [mock_repository]
        mock_project.repositories.filter.return_value = QS([mock_repository])

        mock_project.pull_requests = mock.Mock()

        mock_active_projects = mock.MagicMock()
        mock_active_projects.__iter__.return_value = iter([mock_project])
        mock_active_projects.count.return_value = 1
        mock_active_projects.__getitem__.return_value = [mock_project]
        mock_active_projects.order_by.return_value = mock_active_projects

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
        ):
            command.handle(offset=0)

        mock_project.pull_requests.clear.assert_called_once()

        mock_project.pull_requests.add.assert_called_once_with(
            mock_pr1,
            mock_pr2,
        )
