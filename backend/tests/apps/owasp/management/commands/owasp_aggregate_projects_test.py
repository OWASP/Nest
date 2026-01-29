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

        # Ensure M2M and FK mocks exist for assignment
        project.issues = mock.Mock()
        project.organizations = mock.Mock()
        project.owners = mock.Mock()

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
            # [FIX] Patch Issue to prevent Django ORM from crashing on Mocks
            mock.patch("apps.owasp.management.commands.owasp_aggregate_projects.Issue"),
        ):
            command.handle(offset=offset)

        assert mock_bulk_save.called
        assert mock_print.call_count == projects - offset

        for call in mock_print.call_args_list:
            args, _ = call
            assert "https://owasp.org/www-project-test" in args[0]

    @mock.patch("apps.owasp.management.commands.owasp_aggregate_projects.Issue")
    @mock.patch.object(Project, "bulk_save", autospec=True)
    def test_handle_updates_issues_and_m2m(
        self, mock_bulk_save, mock_issue_model, command, mock_project
    ):
        """Test that issue counts are calculated and M2M fields are updated."""
        mock_projects_list = [mock_project]
        mock_active_projects = mock.MagicMock()
        mock_active_projects.order_by.return_value = mock_active_projects
        mock_active_projects.count.return_value = 1
        mock_active_projects.__iter__.return_value = iter(mock_projects_list)
        mock_active_projects.__getitem__.return_value = mock_projects_list
        mock_aggregate_result = {
            "count": 100,
            "unanswered_count": 20,
            "unassigned_count": 10,
        }
        mock_all_issues_qs = mock.Mock()
        mock_all_issues_qs.aggregate.return_value = mock_aggregate_result

        mock_issue_model.objects.filter.return_value = mock_all_issues_qs

        mock_open_issues_qs = mock.Mock()
        mock_open_issues_qs.filter.return_value.count.return_value = 5

        mock_issue_model.open_issues = mock_open_issues_qs

        mock_repository = mock.Mock()
        mock_repository.organization = None
        mock_repository.latest_release = None

        mock_repository.commits_count = 10
        mock_repository.contributors_count = 5
        mock_repository.forks_count = 2
        mock_repository.open_issues_count = 4
        mock_repository.releases.count.return_value = 1
        mock_repository.stars_count = 50
        mock_repository.subscribers_count = 3
        mock_repository.watchers_count = 7
        mock_repository.top_languages = []
        mock_repository.topics = []

        class QS(list):
            def exists(self):
                return bool(self)

        mock_project.repositories.filter.return_value = QS([mock_repository])

        with (
            mock.patch.object(Project, "active_projects", mock_active_projects),
            mock.patch("builtins.print"),
        ):
            command.handle(offset=0)

        mock_project.issues.clear.assert_called_once()
        mock_project.issues.set.assert_called_once_with(mock_all_issues_qs)

        assert mock_project.issues_count == 100
        assert mock_project.unanswered_issues_count == 20
        assert mock_project.unassigned_issues_count == 10
        assert mock_project.active_issues_count == 5

        assert mock_bulk_save.called
