import sys
from django.utils import timezone
from io import StringIO
from unittest import mock

import pytest

from apps.owasp.management.commands.owasp_update_project_health_metrics import Command
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class TestUpdateProjectHealthMetricsCommand:
    @pytest.fixture()
    def command(self):
        return Command()

    @pytest.fixture()
    def mock_project(self):
        project = mock.Mock(spec=Project)
        project.name = "Test Project"
        project.owasp_url = "https://test.com"
        project.level = Project.ProjectLevel.FLAGSHIP
        project.contributors_count = 5
        project.created_at = timezone.now()
        project.forks_count = 10
        project.stars_count = 100
        project.pushed_at = timezone.now()
        project.released_at = timezone.now()
        project.open_issues_count = 3
        project.releases_count = 5
        project.updated_at = timezone.now()

        project.repositories.all.return_value = []
        project.repositories.aggregate.return_value = {
            "total_prs": 10,
            "open_prs": 2,
            "total_issues": 5,
            "unanswered_issues": 1,
            "unassigned_issues": 1,
            "recent_releases": 2,
        }
        return project

    @pytest.fixture()
    def mock_requirements(self):
        requirements = mock.Mock(spec=ProjectHealthRequirements)
        requirements.contributors_count = 3
        requirements.creation_days = 30
        requirements.forks_count = 5
        requirements.last_release_days = 365
        requirements.last_commit_days = 90
        requirements.open_issues_count = 5
        requirements.open_pull_requests_count = 3
        requirements.owasp_page_update_days = 30
        requirements.last_pull_request_days = 30
        requirements.recent_releases_count = 2
        requirements.stars_count = 50
        requirements.total_pull_requests_count = 20
        requirements.total_releases_count = 5
        requirements.unanswered_issues_count = 3
        requirements.unassigned_issues_count = 3
        requirements.recent_releases_window = 90
        return requirements

    @pytest.mark.parametrize(
        ("offset", "projects"),
        [
            (0, 1),
            (1, 2),
        ],
    )
    @mock.patch(
        "apps.owasp.management.commands.owasp_update_project_health_metrics.ProjectHealthMetrics.objects.bulk_update"
    )
    def test_handle_successful_update(
        self, mock_bulk_update, command, mock_project, mock_requirements, offset, projects
    ):
        """Test successful metrics update for projects."""
        mock_projects = mock.MagicMock()
        mock_projects.__iter__.return_value = iter([mock_project] * projects)
        mock_projects.count.return_value = projects
        mock_projects.order_by.return_value = mock_projects
        mock_projects.__getitem__.return_value = [mock_project]

        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            with (
                mock.patch.object(Project, "active_projects", mock_projects),
                mock.patch.object(
                    ProjectHealthRequirements.objects, "get"
                ) as mock_get_requirements,
                mock.patch.object(
                    ProjectHealthMetrics.objects, "get_or_create"
                ) as mock_metrics_get_or_create,
            ):
                mock_metrics = mock.Mock(spec=ProjectHealthMetrics)
                mock_get_requirements.return_value = mock_requirements
                mock_metrics_get_or_create.return_value = (mock_metrics, True)

                command.handle(offset=offset)

                output = captured_output.getvalue()
                expected_prefix = f"{offset + 1} of {projects}"
                assert expected_prefix in output
                assert mock_bulk_update.called

                expected_fields = [
                    "contributors_count",
                    "created_at",
                    "forks_count",
                    "last_released_at",
                    "last_committed_at",
                    "open_issues_count",
                    "open_pull_requests_count",
                    "owasp_page_last_updated_at",
                    "pull_request_last_created_at",
                    "recent_releases_count",
                    "score",
                    "stars_count",
                    "total_issues_count",
                    "total_pull_request_count",
                    "total_releases_count",
                    "unanswered_issues_count",
                    "unassigned_issues_count",
                ]
                mock_bulk_update.assert_called_once()
                _, kwargs = mock_bulk_update.call_args
                assert kwargs["fields"] == expected_fields
        finally:
            sys.stdout = sys.__stdout__

    @pytest.mark.parametrize(
        "error_message",
        [
            ("Database error"),
            ("Network timeout"),
            ("Invalid data"),
        ],
    )
    def test_handle_exception(self, command, error_message):
        """Test handling of exceptions during update."""
        mock_projects = mock.MagicMock()
        mock_projects.order_by.side_effect = RuntimeError(error_message)

        with (
            mock.patch.object(Project, "active_projects", mock_projects),
            pytest.raises(RuntimeError, match=error_message) as exc_info,
        ):
            command.handle(offset=0)

        assert str(exc_info.value) == error_message
