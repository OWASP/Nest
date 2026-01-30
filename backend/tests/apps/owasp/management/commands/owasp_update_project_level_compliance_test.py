from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.owasp.models.enums.project import ProjectLevel


class TestProjectLevelCompliance(SimpleTestCase):
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.bulk_save"
    )
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.objects"
    )
    @patch("apps.owasp.management.commands.owasp_update_project_level_compliance.requests.get")
    def test_parses_official_level_data(self, mock_get, mock_metrics, mock_bulk_save):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Parsed Project", "repo": "parsed-project", "level": "3.5"}
        ]

        metric = MagicMock()
        metric.project.name = "Parsed Project"
        metric.project.level = ProjectLevel.FLAGSHIP
        metric.level_non_compliant = False

        mock_metrics.select_related.return_value = [metric]

        call_command("owasp_update_project_level_compliance")

        assert metric.level_non_compliant is False
        mock_bulk_save.assert_called_once()

    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.bulk_save"
    )
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.objects"
    )
    @patch("apps.owasp.management.commands.owasp_update_project_level_compliance.requests.get")
    def test_marks_non_compliant_when_levels_differ(self, mock_get, mock_metrics, mock_bulk_save):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Test Project", "repo": "test-project", "level": "4"}
        ]

        metric = MagicMock()
        metric.project.name = "Test Project"
        metric.project.level = ProjectLevel.PRODUCTION
        metric.level_non_compliant = False

        mock_metrics.select_related.return_value = [metric]

        call_command("owasp_update_project_level_compliance")

        assert metric.level_non_compliant is True
        mock_bulk_save.assert_called_once()

    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.bulk_save"
    )
    @patch(
        "apps.owasp.management.commands.owasp_update_project_level_compliance."
        "ProjectHealthMetrics.objects"
    )
    @patch("apps.owasp.management.commands.owasp_update_project_level_compliance.requests.get")
    def test_remains_compliant_when_levels_match(self, mock_get, mock_metrics, mock_bulk_save):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"name": "Test Project", "repo": "test-project", "level": "3"}
        ]

        metric = MagicMock()
        metric.project.name = "Test Project"
        metric.project.level = ProjectLevel.PRODUCTION
        metric.level_non_compliant = False

        mock_metrics.select_related.return_value = [metric]

        call_command("owasp_update_project_level_compliance")

        assert metric.level_non_compliant is False
        mock_bulk_save.assert_called_once()
