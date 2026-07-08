"""Tests for the owasp_enrich_events Django management command."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.owasp.management.commands.owasp_enrich_events import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


class TestOwaspEnrichEventsCommand:
    """Test suite for the owasp_enrich_events command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Enrich events with extra data."

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)
        parser.add_argument.assert_called_once_with(
            "--offset", default=0, required=False, type=int
        )


@patch("apps.owasp.management.commands.owasp_enrich_events.Event")
@patch("apps.owasp.management.commands.owasp_enrich_events.Prompt")
@patch("apps.owasp.management.commands.owasp_enrich_events.time.sleep")
@patch("apps.owasp.management.commands.owasp_enrich_events.logger")
class TestHandleMethod:
    """Test suite for the handle method of the command."""

    @pytest.fixture
    def command(self):
        """Return a command instance with mocked stdout."""
        command = Command()
        command.stdout = MagicMock()

        return command

    def test_full_enrichment(self, mock_logger, mock_sleep, mock_prompt, mock_event, command):
        """Test full enrichment for an event with no data."""
        mock_event_instance = MagicMock(
            latitude=None,
            longitude=None,
            suggested_location=None,
            summary=None,
            url="https://example.com/event",
        )
        mock_event.objects.order_by.return_value.count.return_value = 1
        mock_event.objects.order_by.return_value.__getitem__.return_value = [mock_event_instance]

        mock_summary_prompt = "Summarize this."
        mock_location_prompt = "Where is this?"
        mock_prompt.get_owasp_event_summary.return_value = mock_summary_prompt
        mock_prompt.get_owasp_event_suggested_location.return_value = mock_location_prompt

        command.handle(offset=0)

        mock_event_instance.generate_summary.assert_called_once_with(mock_summary_prompt)
        mock_event_instance.generate_suggested_location.assert_called_once_with(
            prompt=mock_location_prompt
        )
        mock_event_instance.generate_geo_location.assert_called_once()
        mock_sleep.assert_called_once_with(5)
        mock_event.bulk_save.assert_called_once_with(
            [mock_event_instance],
            fields=("latitude", "longitude", "suggested_location", "summary"),
        )

    def test_partial_enrichment_summary_exists(
        self, mock_logger, mock_sleep, mock_prompt, mock_event, command
    ):
        """Test enrichment when summary already exists."""
        mock_event_instance = MagicMock(
            latitude=None,
            longitude=None,
            suggested_location=None,
            summary="Already summarized.",
            url="https://example.com/event",
        )
        mock_event.objects.order_by.return_value.count.return_value = 1
        mock_event.objects.order_by.return_value.__getitem__.return_value = [mock_event_instance]

        command.handle(offset=0)

        mock_event_instance.generate_summary.assert_not_called()
        mock_event_instance.generate_suggested_location.assert_called_once()
        mock_event_instance.generate_geo_location.assert_called_once()

    def test_no_prompts_available(self, mock_logger, mock_sleep, mock_prompt, mock_event, command):
        """Test that generation methods are not called if prompts are not found."""
        mock_prompt.get_owasp_event_summary.return_value = None
        mock_prompt.get_owasp_event_suggested_location.return_value = None

        mock_event_instance = MagicMock(
            summary=None, suggested_location=None, latitude=None, longitude=None
        )
        mock_event.objects.order_by.return_value.count.return_value = 1
        mock_event.objects.order_by.return_value.__getitem__.return_value = [mock_event_instance]

        command.handle(offset=0)

        mock_event_instance.generate_summary.assert_not_called()
        mock_event_instance.generate_suggested_location.assert_not_called()
        mock_event_instance.generate_geo_location.assert_called_once()

    def test_geolocation_exception(
        self, mock_logger, mock_sleep, mock_prompt, mock_event, command
    ):
        """Test that an exception in generate_geo_location is logged."""
        mock_event_instance = MagicMock(
            latitude=None,
            longitude=None,
            suggested_location=None,
            summary=None,
            url="https://example.com/event",
        )
        mock_event.objects.order_by.return_value.count.return_value = 1
        mock_event.objects.order_by.return_value.__getitem__.return_value = [mock_event_instance]

        exception_to_raise = Exception("Geo API failed")
        mock_event_instance.generate_geo_location.side_effect = exception_to_raise

        command.handle(offset=0)

        mock_logger.exception.assert_called_once_with(
            "Could not get geo data for event", extra={"url": mock_event_instance.url}
        )
        mock_sleep.assert_not_called()

    def test_no_events(self, mock_logger, mock_sleep, mock_prompt, mock_event, command):
        """Test command execution with no events."""
        mock_event.objects.order_by.return_value.__getitem__.return_value = []

        command.handle(offset=0)

        mock_event.bulk_save.assert_called_once_with(
            [],
            fields=("latitude", "longitude", "suggested_location", "summary"),
        )
        mock_sleep.assert_not_called()

    def test_offset_argument(self, mock_logger, mock_sleep, mock_prompt, mock_event, command):
        """Test that the offset argument is correctly applied."""
        mock_event.objects.order_by.return_value.count.return_value = 5
        mock_event.objects.order_by.return_value.__getitem__.return_value = []

        command.handle(offset=2)

        mock_event.objects.order_by.return_value.__getitem__.assert_called_once_with(
            slice(2, None)
        )

    def test_all_data_exists(self, mock_logger, mock_sleep, mock_prompt, mock_event, command):
        """Test that no generation methods are called if all data exists."""
        mock_event_instance = MagicMock(
            latitude=1.23,
            longitude=4.56,
            suggested_location="Existing location",
            summary="Existing summary",
        )
        mock_event.objects.order_by.return_value.count.return_value = 1
        mock_event.objects.order_by.return_value.__getitem__.return_value = [mock_event_instance]

        command.handle(offset=0)

        mock_event_instance.generate_summary.assert_not_called()
        mock_event_instance.generate_suggested_location.assert_not_called()
        mock_event_instance.generate_geo_location.assert_not_called()
        mock_sleep.assert_not_called()
        mock_event.bulk_save.assert_called_once_with(
            [mock_event_instance],
            fields=("latitude", "longitude", "suggested_location", "summary"),
        )
