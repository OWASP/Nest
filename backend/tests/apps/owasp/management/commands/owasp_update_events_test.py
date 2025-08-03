"""Tests for the owasp_update_events Django management command."""

from unittest.mock import MagicMock, call, patch

import pytest
from django.core.management.base import BaseCommand

from apps.owasp.management.commands.owasp_update_events import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


class TestOwaspUpdateEventsCommand:
    """Test suite for the owasp_update_events command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Import events from the provided YAML file"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)


@patch("apps.owasp.management.commands.owasp_update_events.get_repository_file_content")
@patch("apps.owasp.management.commands.owasp_update_events.Event")
class TestHandleMethod:
    """Test suite for the handle method of the command."""

    @pytest.fixture
    def command(self):
        """Return a command instance with mocked stdout."""
        command = Command()
        command.stdout = MagicMock()
        return command

    def test_handle_with_valid_data(self, mock_event, mock_get_content, command):
        """Test handle with valid YAML data from the repository."""
        mock_yaml_content = """
        - category: "Global Events"
          events:
            - name: "Global AppSec"
              url: "https://globalappsec.com"
        - category: "Regional Events"
          events:
          - name: "AppSec Conference"
            url: "https://appsecconf.org"
          - name: "AppSec EU"
            url: "https://appseceu.org"
        """
        mock_get_content.return_value = mock_yaml_content

        mock_event1 = MagicMock()
        mock_event2 = MagicMock()
        mock_event3 = MagicMock()
        mock_event.update_data.side_effect = [mock_event1, mock_event2, mock_event3]

        command.handle()

        mock_get_content.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/events.yml"
        )

        assert mock_event.update_data.call_count == 3
        mock_event.update_data.assert_has_calls(
            [
                call(
                    "Global Events",
                    {"name": "Global AppSec", "url": "https://globalappsec.com"},
                    save=False,
                ),
                call(
                    "Regional Events",
                    {"name": "AppSec Conference", "url": "https://appsecconf.org"},
                    save=False,
                ),
                call(
                    "Regional Events",
                    {"name": "AppSec EU", "url": "https://appseceu.org"},
                    save=False,
                ),
            ],
            any_order=True,
        )

        mock_event.bulk_save.assert_called_once_with([mock_event1, mock_event2, mock_event3])

    def test_handle_with_filtered_events(self, mock_event, mock_get_content, command):
        """Test handle when some events are filtered out by update_data returning None."""
        mock_yaml_content = """
        - category: "Global Events"
          events:
            - name: "Valid Event"
              url: "https://valid.com"
            - name: "Invalid Event"
              url: "https://invalid.com"
        """
        mock_get_content.return_value = mock_yaml_content

        mock_valid_event = MagicMock()
        mock_event.update_data.side_effect = [mock_valid_event, None]

        command.handle()

        assert mock_event.update_data.call_count == 2
        mock_event.bulk_save.assert_called_once_with([mock_valid_event])

    def test_handle_with_no_events_in_yaml(self, mock_event, mock_get_content, command):
        """Test handle with YAML data that contains no events."""
        mock_yaml_content = """
        - category: "Global Events"
          events: []
        - category: "Regional Events"
          events: []
        """
        mock_get_content.return_value = mock_yaml_content

        command.handle()

        mock_event.update_data.assert_not_called()
        mock_event.bulk_save.assert_called_once_with([])

    def test_handle_with_empty_yaml_data(self, mock_event, mock_get_content, command):
        """Test handle with empty or invalid YAML data."""
        mock_get_content.return_value = ""
        with patch("yaml.safe_load", return_value=[]):
            command.handle()
        mock_event.update_data.assert_not_called()
        mock_event.bulk_save.assert_called_once_with([])

    def test_handle_with_no_data_from_repo(self, mock_event, mock_get_content, command):
        """Test handle when the repository file is empty."""
        mock_get_content.return_value = None
        with patch("yaml.safe_load", return_value=[]):
            command.handle()
        mock_event.update_data.assert_not_called()
        mock_event.bulk_save.assert_called_once_with([])
