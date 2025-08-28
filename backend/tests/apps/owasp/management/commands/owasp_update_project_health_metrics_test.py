from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
import requests
from django.core.management import call_command
from django.db.models.base import ModelState

from apps.owasp.management.commands.owasp_update_project_health_metrics import Command
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

# Test constants
TEST_PROJECT_NAME = "Test Project"
OWASP_ZAP_NAME = "OWASP ZAP"
OWASP_TOP_TEN_NAME = "OWASP Top 10"
OWASP_TEST_PROJECT_NAME = "OWASP Test Project"
VALID_PROJECT_NAME = "Valid Project"
ANOTHER_VALID_NAME = "Another Valid"
VALID_WITH_NUMBER_NAME = "Valid with number"
PROJECT_FILTER_PATCH = "apps.owasp.models.project.Project.objects.filter"
PROJECT_BULK_SAVE_PATCH = "apps.owasp.models.project.Project.bulk_save"
METRICS_BULK_SAVE_PATCH = "apps.owasp.models.project_health_metrics.ProjectHealthMetrics.bulk_save"
STDOUT_PATCH = "sys.stdout"
FLAGSHIP_LEVEL = "flagship"
PRODUCTION_LEVEL = "production"
LAB_LEVEL = "lab"
INCUBATOR_LEVEL = "incubator"
OTHER_LEVEL = "other"
OWASP_LEVELS_URL = (
    "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/project_levels.json"
)
FETCHING_OFFICIAL_LEVELS_MSG = "Fetching official project levels"
SUCCESSFULLY_FETCHED_MSG = "Successfully fetched"
UPDATED_OFFICIAL_LEVELS_MSG = "Updated official levels for"
EVALUATING_METRICS_MSG = "Evaluating metrics for project:"
NETWORK_ERROR_MSG = "Network error"
INVALID_JSON_ERROR_MSG = "Invalid JSON"
INVALID_FORMAT_ERROR = "Invalid format"
TIMEOUT_30_SECONDS = 30


class TestUpdateProjectHealthMetricsCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with (
            patch(PROJECT_FILTER_PATCH) as projects_patch,
            patch(METRICS_BULK_SAVE_PATCH) as bulk_save_patch,
        ):
            self.mock_projects = projects_patch
            self.mock_bulk_save = bulk_save_patch
            yield

    def test_handle_successful_update(self):
        """Test successful metrics update."""
        test_data = {
            "name": TEST_PROJECT_NAME,
            "contributors_count": 10,
            "created_at": "2023-01-01",
            "forks_count": 2,
            "is_funding_requirements_compliant": True,
            "released_at": "2023-02-01",
            "pushed_at": "2023-03-01",
            "open_issues_count": 1,
            "open_pull_requests_count": 1,
            "owasp_page_last_updated_at": "2023-04-01",
            "pull_request_last_created_at": "2023-05-01",
            "recent_releases_count": 1,
            "stars_count": 100,
            "issues_count": 5,
            "pull_requests_count": 3,
            "releases_count": 2,
            "unanswered_issues_count": 0,
            "unassigned_issues_count": 0,
        }

        # Create mock project with test data
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        for project_field, value in test_data.items():
            setattr(mock_project, project_field, value)

        self.mock_projects.return_value = [mock_project]

        # Set the leaders count to meet compliance
        mock_project.leaders_count = 2

        # Execute command
        with patch(STDOUT_PATCH, new=self.stdout):
            call_command("owasp_update_project_health_metrics")

        self.mock_bulk_save.assert_called_once()
        saved_metrics = self.mock_bulk_save.call_args[0][0]
        assert len(saved_metrics) == 1
        metrics = saved_metrics[0]
        assert isinstance(metrics, ProjectHealthMetrics)
        assert metrics.project == mock_project

        # Verify command output
        assert f"{EVALUATING_METRICS_MSG} {TEST_PROJECT_NAME}" in self.stdout.getvalue()

    @patch("requests.get")
    def test_fetch_official_project_levels_success(self, mock_get):
        """Test successful fetching of official project levels."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": OWASP_ZAP_NAME, "level": FLAGSHIP_LEVEL},
            {"name": OWASP_TOP_TEN_NAME, "level": FLAGSHIP_LEVEL},
            {"name": OWASP_TEST_PROJECT_NAME, "level": PRODUCTION_LEVEL},
            {"name": TEST_PROJECT_NAME, "level": LAB_LEVEL},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=TIMEOUT_30_SECONDS)

        assert result is not None
        assert len(result) == 4
        assert result[OWASP_ZAP_NAME] == FLAGSHIP_LEVEL
        assert result[OWASP_TOP_TEN_NAME] == FLAGSHIP_LEVEL
        assert result[OWASP_TEST_PROJECT_NAME] == PRODUCTION_LEVEL
        assert result[TEST_PROJECT_NAME] == LAB_LEVEL

        # Verify API call
        mock_get.assert_called_once_with(
            OWASP_LEVELS_URL, timeout=TIMEOUT_30_SECONDS, headers={"Accept": "application/json"}
        )

    @patch("requests.get")
    def test_fetch_official_project_levels_http_error(self, mock_get):
        """Test handling of HTTP errors when fetching official levels."""
        mock_get.side_effect = requests.exceptions.RequestException(NETWORK_ERROR_MSG)

        result = self.command.fetch_official_project_levels(timeout=TIMEOUT_30_SECONDS)

        assert result is None

    @patch("requests.get")
    def test_fetch_official_project_levels_invalid_json(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError(INVALID_JSON_ERROR_MSG)
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=TIMEOUT_30_SECONDS)

        assert result is None

    @patch("requests.get")
    def test_fetch_official_project_levels_invalid_format(self, mock_get):
        """Test handling of invalid data format (not a list)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": INVALID_FORMAT_ERROR}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=TIMEOUT_30_SECONDS)

        assert result is None

    @patch("requests.get")
    def test_fetch_official_project_levels_filters_invalid_entries(self, mock_get):
        """Test that invalid entries are filtered out."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": VALID_PROJECT_NAME, "level": FLAGSHIP_LEVEL},
            {"name": "", "level": LAB_LEVEL},  # Empty name should be filtered
            {"level": PRODUCTION_LEVEL},  # Missing name should be filtered
            {"name": ANOTHER_VALID_NAME, "level": INCUBATOR_LEVEL},
            {"name": VALID_WITH_NUMBER_NAME, "level": 3},  # Number level should work
            {"name": "Invalid level"},  # Missing level should be filtered
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.command.fetch_official_project_levels(timeout=TIMEOUT_30_SECONDS)

        assert result is not None
        assert len(result) == 3
        assert result[VALID_PROJECT_NAME] == FLAGSHIP_LEVEL
        assert result[ANOTHER_VALID_NAME] == INCUBATOR_LEVEL
        assert result[VALID_WITH_NUMBER_NAME] == "3"

    def test_update_official_levels_success(self):
        """Test successful update of official levels."""
        # Create mock projects
        project1 = MagicMock(spec=Project)
        project1.name = OWASP_ZAP_NAME
        project1.project_level_official = LAB_LEVEL  # Different from official
        project1._state = ModelState()

        project2 = MagicMock(spec=Project)
        project2.name = OWASP_TOP_TEN_NAME
        project2.project_level_official = FLAGSHIP_LEVEL  # Same as official
        project2._state = ModelState()

        official_levels = {
            OWASP_ZAP_NAME: FLAGSHIP_LEVEL,
            OWASP_TOP_TEN_NAME: FLAGSHIP_LEVEL,
        }

        with (
            patch(PROJECT_FILTER_PATCH) as mock_filter,
            patch(PROJECT_BULK_SAVE_PATCH) as mock_bulk_save,
        ):
            mock_filter.return_value = [project1, project2]

            updated_count = self.command.update_official_levels(official_levels)

            # Only project1 should be updated (different level)
            assert updated_count == 1
            assert project1.project_level_official == FLAGSHIP_LEVEL
            assert project2.project_level_official == FLAGSHIP_LEVEL  # Unchanged

            # Verify bulk_save was called with only the updated project
            mock_bulk_save.assert_called_once()
            saved_projects = mock_bulk_save.call_args[0][0]
            assert len(saved_projects) == 1
            assert saved_projects[0] == project1

    def test_update_official_levels_level_mapping(self):
        """Test that level mapping works correctly."""
        project = MagicMock(spec=Project)
        project.name = TEST_PROJECT_NAME
        project.project_level_official = OTHER_LEVEL
        project._state = ModelState()

        test_cases = [
            ("2", INCUBATOR_LEVEL),
            ("3", LAB_LEVEL),
            ("3.5", PRODUCTION_LEVEL),
            ("4", FLAGSHIP_LEVEL),
            (INCUBATOR_LEVEL, INCUBATOR_LEVEL),
            (LAB_LEVEL, LAB_LEVEL),
            (PRODUCTION_LEVEL, PRODUCTION_LEVEL),
            (FLAGSHIP_LEVEL, FLAGSHIP_LEVEL),
            ("unknown", OTHER_LEVEL),
        ]

        for official_level, expected_mapped in test_cases:
            with (
                patch(PROJECT_FILTER_PATCH) as mock_filter,
                patch(PROJECT_BULK_SAVE_PATCH) as mock_bulk_save,
            ):
                mock_filter.return_value = [project]
                project.project_level_official = OTHER_LEVEL  # Reset

                official_levels = {TEST_PROJECT_NAME: official_level}
                updated_count = self.command.update_official_levels(official_levels)

                assert project.project_level_official == expected_mapped
                if expected_mapped != OTHER_LEVEL:  # Only count as update if level changed
                    assert updated_count == 1
                    mock_bulk_save.assert_called_once()
                else:
                    assert updated_count == 0

    @patch("requests.get")
    def test_handle_with_official_levels_integration(self, mock_get):
        """Test complete integration with official levels fetching."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": TEST_PROJECT_NAME, "level": FLAGSHIP_LEVEL},
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock project
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        mock_project.name = TEST_PROJECT_NAME
        mock_project.project_level_official = LAB_LEVEL  # Different from official
        for field in [
            "contributors_count",
            "created_at",
            "forks_count",
            "is_funding_requirements_compliant",
            "is_leader_requirements_compliant",
            "pushed_at",
            "released_at",
            "open_issues_count",
            "open_pull_requests_count",
            "owasp_page_last_updated_at",
            "pull_request_last_created_at",
            "recent_releases_count",
            "stars_count",
            "issues_count",
            "pull_requests_count",
            "releases_count",
            "unanswered_issues_count",
            "unassigned_issues_count",
        ]:
            setattr(mock_project, field, 0)

        with (
            patch(PROJECT_FILTER_PATCH) as mock_projects,
            patch(PROJECT_BULK_SAVE_PATCH),
            patch(METRICS_BULK_SAVE_PATCH),
            patch(STDOUT_PATCH, new=self.stdout),
        ):
            mock_projects.return_value = [mock_project]

            call_command("owasp_update_project_health_metrics")

            # Verify official levels were fetched and updated
            assert FETCHING_OFFICIAL_LEVELS_MSG in self.stdout.getvalue()
            success_msg = f"{SUCCESSFULLY_FETCHED_MSG} 1 official project levels"
            assert success_msg in self.stdout.getvalue()
            assert f"{UPDATED_OFFICIAL_LEVELS_MSG} 1 projects" in self.stdout.getvalue()

            # Verify project was updated with official level
            assert mock_project.project_level_official == FLAGSHIP_LEVEL

    def test_handle_sync_official_levels_only(self):
        """Test command with --sync-official-levels-only flag."""
        # Create mock project
        mock_project = MagicMock(spec=Project)
        mock_project.name = TEST_PROJECT_NAME
        mock_project.project_level_official = LAB_LEVEL  # Different from official
        mock_project._state = ModelState()

        with (
            patch(PROJECT_FILTER_PATCH) as mock_filter,
            patch(PROJECT_BULK_SAVE_PATCH) as mock_bulk_save,
            patch("requests.get") as mock_get,
            patch(STDOUT_PATCH, new=self.stdout),
        ):
            # Mock API response
            mock_response = MagicMock()
            mock_response.json.return_value = [
                {"name": TEST_PROJECT_NAME, "level": FLAGSHIP_LEVEL}
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            mock_filter.return_value = [mock_project]

            call_command("owasp_update_project_health_metrics", "--sync-official-levels-only")

            # Verify official levels were synced
            output = self.stdout.getvalue()
            assert "Official level sync completed." in output
            # Health metrics should be skipped
            assert "Evaluating metrics for project" not in output

            # Verify project was updated
            assert mock_project.project_level_official == FLAGSHIP_LEVEL
            mock_bulk_save.assert_called_once()

    def test_handle_skip_official_levels(self):
        """Test command with --skip-official-levels flag."""
        mock_project = MagicMock(spec=Project)
        mock_project._state = ModelState()
        mock_project.name = TEST_PROJECT_NAME
        for field in [
            "contributors_count",
            "created_at",
            "forks_count",
            "is_funding_requirements_compliant",
            "is_leader_requirements_compliant",
            "pushed_at",
            "released_at",
            "open_issues_count",
            "open_pull_requests_count",
            "owasp_page_last_updated_at",
            "pull_request_last_created_at",
            "recent_releases_count",
            "stars_count",
            "issues_count",
            "pull_requests_count",
            "releases_count",
            "unanswered_issues_count",
            "unassigned_issues_count",
        ]:
            setattr(mock_project, field, 0)

        with (
            patch(PROJECT_FILTER_PATCH) as mock_projects,
            patch(METRICS_BULK_SAVE_PATCH),
            patch(STDOUT_PATCH, new=self.stdout),
        ):
            mock_projects.return_value = [mock_project]

            call_command("owasp_update_project_health_metrics", "--skip-official-levels")

            # Verify official levels fetching was skipped
            output = self.stdout.getvalue()
            assert FETCHING_OFFICIAL_LEVELS_MSG not in output
            assert f"{EVALUATING_METRICS_MSG} {TEST_PROJECT_NAME}" in output
