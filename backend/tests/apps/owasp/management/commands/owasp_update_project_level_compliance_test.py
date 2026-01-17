from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.owasp.models.enums.project import ProjectLevel


class TestProjectLevelCompliance(SimpleTestCase):
    @patch("apps.owasp.management.commands.owasp_update_project_level_compliance.requests.get")
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.get_latest_health_metrics"
    )
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.bulk_save"
    )
    def test_marks_project_as_non_compliant_when_levels_differ(
        self, mock_bulk_save, mock_get_latest, mock_get
    ):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Test Project", "repo": "test-project", "level": "4"}
        ]

        metric = MagicMock()
        metric.project.name = "Test Project"
        metric.project.level = ProjectLevel.PRODUCTION
        metric.project.owasp_url = None
        metric.level_non_compliant = False

        mock_get_latest.return_value.select_related.return_value = [metric]

        call_command("owasp_update_project_level_compliance")

        assert metric.level_non_compliant is True
        mock_bulk_save.assert_called_once()

    @patch("apps.owasp.management.commands.owasp_update_project_level_compliance.requests.get")
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.get_latest_health_metrics"
    )
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.bulk_save"
    )
    def test_project_remains_compliant_when_levels_match(
        self, mock_bulk_save, mock_get_latest, mock_get
    ):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Test Project", "repo": "test-project", "level": "3"}
        ]

        metric = MagicMock()
        metric.project.name = "Test Project"
        metric.project.level = ProjectLevel.PRODUCTION
        metric.project.owasp_url = None
        metric.level_non_compliant = False

        mock_get_latest.return_value.select_related.return_value = [metric]

        call_command("owasp_update_project_level_compliance")

        assert metric.level_non_compliant is False
        mock_bulk_save.assert_called_once()
