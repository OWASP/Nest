"""Tests for the owasp_update_events management command."""

from unittest.mock import patch

import pytest
import yaml
from django.core.management import call_command

from apps.owasp.management.commands.owasp_update_events import Command
from apps.owasp.models.event import Event

EXPECTED_EVENT_COUNT = 3


@pytest.fixture()
def mock_yaml_data():
    """Return mock YAML data for events."""
    return [
        {
            "category": "Global Events",
            "events": [
                {
                    "name": "Global AppSec Dublin",
                    "date": "February 15-17, 2023",
                    "url": "https://example.com/event1",
                },
                {
                    "name": "Global AppSec Washington DC",
                    "date": "October 18-20, 2023",
                    "url": "https://example.com/event2",
                },
            ],
        },
        {
            "category": "Regional Events",
            "events": [
                {
                    "name": "OWASP Virtual AppSec Indonesia",
                    "date": "September 8, 2023",
                    "url": "https://example.com/event3",
                },
            ],
        },
    ]


class TestOwaspUpdateEvents:
    """Test suite for owasp_update_events command."""

    @patch("apps.owasp.management.commands.owasp_update_events.get_repository_file_content")
    @patch.object(Event, "bulk_save")
    @patch.object(Event, "update_data")
    def test_handle_with_valid_data(
        self, mock_update_data, mock_bulk_save, mock_get_content, mock_yaml_data
    ):
        """Test command execution with valid data."""
        mock_get_content.return_value = yaml.dump(mock_yaml_data)
        mock_update_data.side_effect = lambda category, event_data: {
            "category": category,
            "data": event_data,
        }

        with patch("django.db.connection"):
            call_command("owasp_update_events")

        mock_get_content.assert_called_once_with(
            "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/events.yml"
        )

        assert mock_update_data.call_count == EXPECTED_EVENT_COUNT
        mock_update_data.assert_any_call("Global Events", mock_yaml_data[0]["events"][0])
        mock_update_data.assert_any_call("Global Events", mock_yaml_data[0]["events"][1])
        mock_update_data.assert_any_call("Regional Events", mock_yaml_data[1]["events"][0])

        expected_data = [
            {"category": "Global Events", "data": mock_yaml_data[0]["events"][0]},
            {"category": "Global Events", "data": mock_yaml_data[0]["events"][1]},
            {"category": "Regional Events", "data": mock_yaml_data[1]["events"][0]},
        ]
        mock_bulk_save.assert_called_once_with(expected_data)

    @patch("apps.owasp.management.commands.owasp_update_events.get_repository_file_content")
    @patch.object(Event, "bulk_save")
    def test_handle_with_empty_data(self, mock_bulk_save, mock_get_content):
        """Test command execution with empty data."""
        mock_get_content.return_value = yaml.dump([])

        with patch("django.db.connection"):
            call_command("owasp_update_events")

        mock_bulk_save.assert_called_once_with([])

    @patch("apps.owasp.management.commands.owasp_update_events.get_repository_file_content")
    @patch.object(Event, "bulk_save")
    def test_handle_with_no_events(self, mock_bulk_save, mock_get_content):
        """Test command execution with categories but no events."""
        mock_data = [{"category": "Test Category", "events": []}]
        mock_get_content.return_value = yaml.dump(mock_data)

        with patch("django.db.connection"):
            call_command("owasp_update_events")

        mock_bulk_save.assert_called_once_with([])

    @patch("apps.owasp.management.commands.owasp_update_events.get_repository_file_content")
    @patch("yaml.safe_load")
    @patch.object(Event, "bulk_save")
    def test_handle_with_yaml_error(self, mock_bulk_save, mock_yaml_load, mock_get_content):
        """Test command execution with YAML parsing error."""
        mock_get_content.return_value = "invalid: yaml: content:"
        mock_yaml_load.side_effect = yaml.YAMLError("Invalid YAML")

        with pytest.raises(yaml.YAMLError, match="Invalid YAML"), patch("django.db.connection"):
            call_command("owasp_update_events")

        mock_bulk_save.assert_not_called()

    def test_command_help_text(self):
        """Test the command help text."""
        cmd = Command()
        assert cmd.help == "Import events from the provided YAML file"
