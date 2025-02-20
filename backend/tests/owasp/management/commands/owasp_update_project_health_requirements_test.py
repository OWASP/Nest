from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.owasp.management.commands.owasp_update_project_health_requirements import Command
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_requirements import ProjectHealthRequirements


class TestUpdateProjectHealthRequirementsCommand:
    @pytest.fixture(autouse=True)
    def _setup(self):
        """Set up test environment."""
        self.stdout = StringIO()
        self.command = Command()
        with patch(
            "apps.owasp.models.project_health_requirements.ProjectHealthRequirements.objects"
        ) as requirements_patch:
            self.mock_requirements = requirements_patch
            yield

    @pytest.mark.parametrize(
        ("level", "expected_output", "display_name"),
        [
            (
                "flagship",
                "Created health requirements for Flagship projects",
                "Flagship",
            ),
            (
                "incubator",
                "Created health requirements for Incubator projects",
                "Incubator",
            ),
            (None, "Created default health requirements for Flagship projects", "Flagship"),
        ],
    )
    def test_handle_successful_creation(self, level, expected_output, display_name):
        """Test successful requirements creation."""
        mock_requirements = MagicMock(spec=ProjectHealthRequirements)
        mock_requirements.get_level_display.return_value = display_name
        self.mock_requirements.get_or_create.return_value = (mock_requirements, True)

        with patch("sys.stdout", new=StringIO()) as fake_out:
            if level:
                call_command("owasp_update_project_health_requirements", level=level)
            else:
                call_command("owasp_update_project_health_requirements")

            assert expected_output in fake_out.getvalue()

    def test_handle_exception(self):
        """Test handling of exceptions during update."""
        error_message = "Database error"
        self.mock_requirements.get_or_create.side_effect = CommandError(error_message)

        with pytest.raises(CommandError, match=error_message) as exc_info:
            call_command("owasp_update_project_health_requirements")

        assert str(exc_info.value) == error_message

    @pytest.mark.parametrize(
        "level",
        [
            Project.ProjectLevel.FLAGSHIP,
            Project.ProjectLevel.INCUBATOR,
            Project.ProjectLevel.LAB,
            Project.ProjectLevel.PRODUCTION,
            Project.ProjectLevel.OTHER,
        ],
    )
    def test_get_default_requirements(self, level):
        """Test default requirements generation for different project levels."""
        defaults = self.command.get_default_requirements(level)

        assert isinstance(defaults, dict)
        assert "contributors_count" in defaults
        assert "creation_days" in defaults
        assert "forks_count" in defaults
        assert "last_release_days" in defaults
        assert "last_commit_days" in defaults
