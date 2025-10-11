"""Tests for the owasp_check_project_level_compliance Django management command."""

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from django.test import TestCase

from apps.owasp.management.commands.owasp_check_project_level_compliance import Command
from apps.owasp.models.enums.project import ProjectLevel
from apps.owasp.models.project import Project


class TestCheckProjectLevelComplianceCommand(TestCase):
    """Test suite for the owasp_check_project_level_compliance command."""

    def setUp(self):
        """Set up test fixtures."""
        # Initialize command instance
        self.command = Command()

        # Create test projects with different compliance statuses
        self.compliant_project = Project.objects.create(
            key="www-project-compliant-test",
            name="Compliant Test Project",
            level=ProjectLevel.LAB,
            is_level_compliant=True,
            is_active=True,
        )

        self.non_compliant_project = Project.objects.create(
            key="www-project-non-compliant-test",
            name="Non-Compliant Test Project",
            level=ProjectLevel.PRODUCTION,
            is_level_compliant=True,  # Will be marked as non-compliant during test
            is_active=True,
        )

        self.not_in_list_project = Project.objects.create(
            key="www-project-unlisted-test",
            name="Unlisted Test Project",
            level=ProjectLevel.INCUBATOR,
            is_level_compliant=True,
            is_active=True,
        )

    def test_fetch_official_project_levels_success(self):
        """Test successfully fetching and parsing project levels JSON."""
        mock_json_data = {
            "compliant-test": "lab",
            "non-compliant-test": "lab",
            "another-project": "flagship",
        }

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            result = self.command.fetch_official_project_levels()

        assert result == mock_json_data
        assert len(result) == 3
        assert result["compliant-test"] == "lab"

    def test_fetch_official_project_levels_failure(self):
        """Test handling of fetch failures."""
        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network error")

            result = self.command.fetch_official_project_levels()

        assert result == {}

    @pytest.mark.parametrize(
        ("input_level", "expected_level"),
        [
            ("Incubator", "incubator"),
            ("LAB", "lab"),
            ("Production", "production"),
            ("flagship", "flagship"),
            ("Labs", "lab"),  # Plural form
            ("Incubators", "incubator"),  # Plural form
            ("Unknown", "other"),  # Unknown level
            ("", "other"),  # Empty string
        ],
    )
    def test_normalize_level(self, input_level, expected_level):
        """Test level normalization with various inputs."""
        result = self.command.normalize_level(input_level)
        assert result == expected_level

    def test_handle_compliant_project(self):
        """Test that compliant projects remain compliant."""
        mock_json_data = {
            "compliant-test": "lab",
        }

        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            call_command("owasp_check_project_level_compliance", stdout=out)

        # Refresh from database
        self.compliant_project.refresh_from_db()

        # Assert project remains compliant
        assert self.compliant_project.is_level_compliant is True

    def test_handle_non_compliant_project_level_mismatch(self):
        """Test that projects with level mismatches are marked non-compliant."""
        mock_json_data = {
            "non-compliant-test": "lab",  # Mismatch: project has "production"
        }

        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            call_command("owasp_check_project_level_compliance", stdout=out)

        # Refresh from database
        self.non_compliant_project.refresh_from_db()

        # Assert project is marked non-compliant
        assert self.non_compliant_project.is_level_compliant is False

        # Check output contains warning
        output = out.getvalue()
        assert "Level mismatch" in output

    def test_handle_project_not_in_official_list(self):
        """Test that projects not in the official list are marked non-compliant."""
        mock_json_data = {
            "compliant-test": "lab",
            "non-compliant-test": "production",
            # unlisted-test is not in the official list
        }

        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            call_command("owasp_check_project_level_compliance", stdout=out)

        # Refresh from database
        self.not_in_list_project.refresh_from_db()

        # Assert project is marked non-compliant
        assert self.not_in_list_project.is_level_compliant is False

        # Check output
        output = out.getvalue()
        assert "Not found in official list" in output

    def test_handle_dry_run_mode(self):
        """Test that dry-run mode doesn't update the database."""
        mock_json_data = {
            "non-compliant-test": "lab",  # Mismatch
        }

        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            call_command("owasp_check_project_level_compliance", "--dry-run", stdout=out)

        # Refresh from database
        self.non_compliant_project.refresh_from_db()

        # Assert project is still marked as compliant (no database update)
        assert self.non_compliant_project.is_level_compliant is True

        # Check output indicates dry run
        output = out.getvalue()
        assert "DRY RUN" in output
        assert "Would update" in output

    def test_handle_fetch_failure(self):
        """Test handling when fetching official levels fails."""
        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_urlopen.side_effect = Exception("Network error")

            call_command("owasp_check_project_level_compliance", stdout=out)

        # Check that command handles failure gracefully
        output = out.getvalue()
        assert "Failed to fetch" in output or "Could not fetch" in output

    def test_compliance_summary_output(self):
        """Test that the command outputs a proper compliance summary."""
        mock_json_data = {
            "compliant-test": "lab",
            "non-compliant-test": "lab",
        }

        out = StringIO()

        with patch(
            "apps.owasp.management.commands.owasp_check_project_level_compliance.urlopen"
        ) as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(mock_json_data).encode("utf-8")
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response

            call_command("owasp_check_project_level_compliance", stdout=out)

        output = out.getvalue()

        # Check for summary section
        assert "COMPLIANCE SUMMARY" in output
        assert "Total Projects" in output
        assert "Compliant" in output
        assert "Non-Compliant" in output

    def test_add_arguments(self):
        """Test that command accepts --dry-run argument."""
        from django.core.management import CommandParser

        parser = CommandParser()
        command = Command()
        command.add_arguments(parser)

        # Verify --dry-run argument is registered
        options = parser.parse_args(["--dry-run"])
        assert options.dry_run is True

        options = parser.parse_args([])
        assert options.dry_run is False
