"""Tests for event content extractor."""

from datetime import date
from unittest.mock import MagicMock

from apps.ai.common.extractors.event import extract_event_content


class TestEventExtractor:
    """Test cases for event content extraction."""

    def test_extract_event_content_full_data(self):
        """Test extraction with complete event data."""
        event = MagicMock()
        event.description = "Test event description"
        event.summary = "Test event summary"
        event.name = "Test Event"
        event.category = "conference"
        event.get_category_display.return_value = "Conference"
        event.start_date = date(2024, 6, 15)
        event.end_date = date(2024, 6, 17)
        event.suggested_location = "San Francisco, CA"
        event.latitude = 37.7749
        event.longitude = -122.4194
        event.url = "https://event.example.com"

        prose, metadata = extract_event_content(event)

        assert "Description: Test event description" in prose
        assert "Summary: Test event summary" in prose

        assert "Event Name: Test Event" in metadata
        assert "Category: Conference" in metadata
        assert "Start Date: 2024-06-15" in metadata
        assert "End Date: 2024-06-17" in metadata
        assert "Location: San Francisco, CA" in metadata
        assert "Coordinates: 37.7749, -122.4194" in metadata
        assert "Event URL: https://event.example.com" in metadata

    def test_extract_event_content_minimal_data(self):
        """Test extraction with minimal event data."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "Minimal Event"
        event.category = None
        event.start_date = None
        event.end_date = None
        event.suggested_location = None
        event.latitude = None
        event.longitude = None
        event.url = None

        prose, metadata = extract_event_content(event)

        assert prose == ""
        assert "Event Name: Minimal Event" in metadata
        assert "Category:" not in metadata
        assert "Start Date:" not in metadata
        assert "End Date:" not in metadata
        assert "Location:" not in metadata
        assert "Coordinates:" not in metadata
        assert "Event URL:" not in metadata

    def test_extract_event_content_empty_strings(self):
        """Test extraction with empty string fields."""
        event = MagicMock()
        event.description = ""
        event.summary = ""
        event.name = ""
        event.category = ""
        event.get_category_display.return_value = ""
        event.start_date = None
        event.end_date = None
        event.suggested_location = ""
        event.latitude = None
        event.longitude = None
        event.url = ""

        prose, metadata = extract_event_content(event)

        assert prose == ""
        assert metadata == ""

    def test_extract_event_content_only_latitude(self):
        """Test extraction with only latitude (no coordinates)."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "Test Event"
        event.category = None
        event.start_date = None
        event.end_date = None
        event.suggested_location = None
        event.latitude = 37.7749
        event.longitude = None
        event.url = None

        prose, metadata = extract_event_content(event)

        assert prose == ""
        assert "Event Name: Test Event" in metadata
        assert "Coordinates:" not in metadata

    def test_extract_event_content_only_longitude(self):
        """Test extraction with only longitude (no coordinates)."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "Test Event"
        event.category = None
        event.start_date = None
        event.end_date = None
        event.suggested_location = None
        event.latitude = None
        event.longitude = -122.4194
        event.url = None

        prose, metadata = extract_event_content(event)

        assert prose == ""
        assert "Event Name: Test Event" in metadata
        assert "Coordinates:" not in metadata

    def test_extract_event_content_zero_coordinates(self):
        """Test extraction with zero coordinates (should be included)."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "Test Event"
        event.category = None
        event.start_date = None
        event.end_date = None
        event.suggested_location = None
        event.latitude = 0.0
        event.longitude = 0.0
        event.url = None

        _, metadata = extract_event_content(event)

        assert "Event Name: Test Event" in metadata
        assert "Coordinates: 0.0, 0.0" in metadata

    def test_extract_event_content_partial_dates(self):
        """Test extraction with only start date."""
        event = MagicMock()
        event.description = "Event with start date only"
        event.summary = None
        event.name = "Partial Event"
        event.category = "workshop"
        event.get_category_display.return_value = "Workshop"
        event.start_date = date(2024, 8, 1)
        event.end_date = None
        event.suggested_location = "Online"
        event.latitude = None
        event.longitude = None
        event.url = "https://online-event.com"

        prose, metadata = extract_event_content(event)

        assert "Description: Event with start date only" in prose
        assert "Event Name: Partial Event" in metadata
        assert "Category: Workshop" in metadata
        assert "Start Date: 2024-08-01" in metadata
        assert "End Date:" not in metadata
        assert "Location: Online" in metadata
        assert "Event URL: https://online-event.com" in metadata

    def test_extract_event_content_only_end_date(self):
        """Test extraction with only end date."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "End Date Event"
        event.category = None
        event.start_date = None
        event.end_date = date(2024, 12, 25)
        event.suggested_location = None
        event.latitude = None
        event.longitude = None
        event.url = None

        prose, metadata = extract_event_content(event)

        assert prose == ""
        assert "Event Name: End Date Event" in metadata
        assert "Start Date:" not in metadata
        assert "End Date: 2024-12-25" in metadata

    def test_extract_event_content_category_display_method(self):
        """Test that get_category_display method is called properly."""
        event = MagicMock()
        event.description = None
        event.summary = None
        event.name = "Category Test Event"
        event.category = "meetup"
        event.get_category_display.return_value = "Meetup"
        event.start_date = None
        event.end_date = None
        event.suggested_location = None
        event.latitude = None
        event.longitude = None
        event.url = None

        _, metadata = extract_event_content(event)

        event.get_category_display.assert_called_once()
        assert "Category: Meetup" in metadata
