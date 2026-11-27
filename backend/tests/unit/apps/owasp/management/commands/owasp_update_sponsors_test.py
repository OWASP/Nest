"""Tests for the owasp_update_sponsors Django management command."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.owasp.management.commands.owasp_update_sponsors import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


class TestOwaspUpdateSponsorsCommand:
    """Test suite for the owasp_update_sponsors command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Import sponsors from the provided YAML file"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)


@patch("apps.owasp.management.commands.owasp_update_sponsors.get_repository_file_content")
@patch("apps.owasp.management.commands.owasp_update_sponsors.Sponsor")
class TestHandleMethod:
    """Test suite for the handle method of the command."""

    @pytest.fixture
    def command(self):
        """Return a command instance."""
        return Command()

    def test_handle_with_valid_data(self, mock_sponsor, mock_get_content, command):
        """Test handle with valid YAML data from the repository."""
        mock_yaml_content = """
        - name: Sponsor One
          url: https://sponsor.one
        - name: Sponsor Two
          url: https://sponsor.two
        """
        mock_get_content.return_value = mock_yaml_content

        mock_sponsor1 = MagicMock()
        mock_sponsor2 = MagicMock()
        mock_sponsor.update_data.side_effect = [mock_sponsor1, mock_sponsor2]

        command.handle()

        mock_get_content.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/corp_members.yml"
        )
        assert mock_sponsor.update_data.call_count == 2
        mock_sponsor.bulk_save.assert_called_once_with([mock_sponsor1, mock_sponsor2])

    def test_handle_with_filtered_sponsors(self, mock_sponsor, mock_get_content, command):
        """Test handle when some sponsors are filtered out by update_data returning None."""
        mock_get_content.return_value = (
            "- name: Valid Sponsor\n"
            "  url: https://valid.com\n"
            "- name: Invalid Sponsor\n"
            "  url: https://invalid.com\n"
        )
        mock_valid_sponsor = MagicMock()
        mock_sponsor.update_data.side_effect = [mock_valid_sponsor, None]

        command.handle()

        assert mock_sponsor.update_data.call_count == 2
        mock_sponsor.bulk_save.assert_called_once_with([mock_valid_sponsor, None])

    def test_handle_with_no_sponsors_in_yaml(self, mock_sponsor, mock_get_content, command):
        """Test handle with YAML data that contains no sponsors."""
        mock_get_content.return_value = "[]"

        with patch("yaml.safe_load", return_value=[]):
            command.handle()

        mock_sponsor.update_data.assert_not_called()
        mock_sponsor.bulk_save.assert_called_once_with([])

    def test_handle_with_empty_yaml_data(self, mock_sponsor, mock_get_content, command):
        """Test handle with empty YAML data."""
        mock_get_content.return_value = ""

        with patch("yaml.safe_load", return_value=[]):
            command.handle()

        mock_sponsor.update_data.assert_not_called()
        mock_sponsor.bulk_save.assert_called_once_with([])

    def test_handle_with_no_data_from_repo(self, mock_sponsor, mock_get_content, command):
        """Test handle when the repository file is empty."""
        mock_get_content.return_value = ""

        with patch("yaml.safe_load", return_value=[]):
            command.handle()

        mock_sponsor.update_data.assert_not_called()
        mock_sponsor.bulk_save.assert_called_once_with([])
