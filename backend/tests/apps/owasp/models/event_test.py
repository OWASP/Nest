from datetime import UTC, date
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone

from apps.owasp.models.event import Event


class TestEventModel:
    @pytest.mark.parametrize(
        ("name", "key", "expected_str"),
        [
            ("event1", "", "event1"),
            ("", "key1", "key1"),
            ("", "", ""),
        ],
    )
    def test_event_str(self, name, key, expected_str):
        event = Event(name=name, key=key, start_date=date(2025, 1, 1))
        assert str(event) == expected_str

    def test_bulk_save(self):
        mock_event = [
            Mock(id=None, start_date=date(2025, 1, 1)),
            Mock(id=1, start_date=date(2025, 1, 1)),
        ]
        with patch("apps.owasp.models.event.BulkSaveModel.bulk_save") as mock_bulk_save:
            Event.bulk_save(mock_event, fields=["name"])
            mock_bulk_save.assert_called_once_with(Event, mock_event, fields=["name"])

    @pytest.mark.parametrize(
        ("dates", "start_date", "expected_result"),
        [
            # Test case: None or empty dates
            (None, date(2025, 5, 26), None),
            ("", date(2025, 5, 26), None),
            # Test case: Single-day events
            ("June 5, 2025", date(2025, 6, 5), date(2025, 6, 5)),
            ("June 19, 2025", date(2025, 6, 19), date(2025, 6, 19)),
            # Test case: Date ranges with proper format
            ("May 26-30, 2025", date(2025, 5, 26), date(2025, 5, 30)),
            ("November 3-7, 2025", date(2025, 11, 3), date(2025, 11, 7)),
            ("November 2-6, 2026", date(2026, 11, 2), date(2026, 11, 6)),
            ("September 2-5, 2025", date(2025, 9, 2), date(2025, 9, 5)),
            ("September 12-13, 2025", date(2025, 9, 12), date(2025, 9, 13)),
            ("October 21-24, 2025", date(2025, 10, 21), date(2025, 10, 24)),
            ("November 19-20, 2025", date(2025, 11, 19), date(2025, 11, 20)),
            ("December 2-3, 2025", date(2025, 12, 2), date(2025, 12, 3)),
            # Test case: Special format with spaces in date ranges
            (
                "May 25 - 28, 2025",
                date(2025, 5, 25),
                date(2025, 5, 28),
            ),
            # Test edge cases
            ("Invalid date", None, None),  # Invalid date format
            ("May 26-invalid, 2025", date(2025, 5, 26), None),  # Invalid day in range
            ("May, 2025", None, None),  # Missing day
        ],
    )
    def test_parse_dates(self, dates, start_date, expected_result):
        with patch("apps.owasp.models.event.parser.parse") as mock_parse:
            if expected_result is not None:
                mock_date = Mock()
                mock_date.date.return_value = expected_result
                mock_parse.return_value = mock_date
            elif dates and ("Invalid" in dates or dates in {"May, 2025"}):
                mock_parse.side_effect = ValueError("Invalid date")
            else:
                mock_date = Mock()
                mock_date.date.return_value = date(2025, 1, 1)
                mock_parse.return_value = mock_date

            result = Event.parse_dates(dates, start_date)
            assert result == expected_result

    @pytest.mark.parametrize(
        ("dates", "start_date", "expected_result"),
        [
            ("June 5, 2025", date(2025, 6, 5), date(2025, 6, 5)),
            ("May 26-30, 2025", date(2025, 5, 26), date(2025, 5, 30)),
            ("November 3-7, 2025", date(2025, 11, 3), date(2025, 11, 7)),
            ("September 2-5, 2025", date(2025, 9, 2), date(2025, 9, 5)),
            ("October 21-24, 2025", date(2025, 10, 21), date(2025, 10, 24)),
        ],
    )
    def test_parse_dates_integration(self, dates, start_date, expected_result):
        """Test parse_dates with real parser (no mocking)."""
        result = Event.parse_dates(dates, start_date)
        assert result == expected_result

    def test_parse_dates_with_space_in_range(self):
        """Test the edge case with spaces in date range that's currently handled."""
        dates = "May 25 - 28, 2025"
        start_date = date(2025, 5, 25)

        result = Event.parse_dates(dates, start_date)
        assert result == date(2025, 5, 28)

    def test_update_data_existing_event(self):
        """Test update_data when the event already exists."""
        category = "Global"
        data = {
            "name": "Test Event",
            "start-date": "2025-05-26",
            "dates": "May 26-30, 2025",
            "optional-text": "Description text",
            "url": "https://example.com",
        }

        with (
            patch("apps.owasp.models.event.slugify") as mock_slugify,
            patch("apps.owasp.models.event.Event.objects.get") as mock_get,
            patch("apps.owasp.models.event.Event.parse_dates") as mock_parse_dates,
            patch("apps.owasp.models.event.parser.parse") as mock_parser,
        ):
            mock_slugify.return_value = "test-event"

            mock_parse_dates.return_value = date(2025, 5, 30)

            mock_date = Mock()
            mock_date.date.return_value = date(2025, 5, 26)
            mock_parser.return_value = mock_date

            mock_event = Mock()
            mock_get.return_value = mock_event

            result = Event.update_data(category, data)

            mock_slugify.assert_called_once_with(data["name"])
            mock_get.assert_called_once_with(key="test-event")
            mock_event.from_dict.assert_called_once_with(category, data)
            mock_event.save.assert_called_once()
            assert result == mock_event

    @patch("apps.owasp.models.event.Event.objects.filter")
    def test_parse_google_calendar_event(self, mock_filter):
        """Test the parsing of Google Calendar event."""
        event_dict = {
            "id": "12345",
            "summary": "Google Calendar Event",
            "start": {
                "dateTime": "2025-05-26T09:00:00-07:00",
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": "2025-05-30T16:00:00-07:00",
                "timeZone": "America/Los_Angeles",
            },
            "status": "confirmed",
        }

        mock_filter.return_value.first.return_value = None
        event = Event.parse_google_calendar_event(event_dict)
        assert isinstance(event, Event)
        assert event.name == "Google Calendar Event"
        assert event.google_calendar_id == "12345"
        assert event.start_date == timezone.datetime(2025, 5, 26, 16, 0, 0, tzinfo=UTC)
        assert event.end_date == timezone.datetime(2025, 5, 30, 23, 0, 0, tzinfo=UTC)

    @patch("apps.owasp.models.event.Event.objects.filter")
    def test_parse_existing_google_calendar_event(self, mock_filter):
        """Test parsing when the event already exists."""
        event_dict = {
            "id": "12345",
            "summary": "Existing Google Calendar Event",
            "start": {
                "dateTime": "2025-05-26T09:00:00-07:00",
                "timeZone": "America/Los_Angeles",
            },
            "end": {
                "dateTime": "2025-05-30T16:00:00-07:00",
                "timeZone": "America/Los_Angeles",
            },
            "status": "confirmed",
        }

        mock_existing_event = Mock(spec=Event)
        mock_filter.return_value.first.return_value = mock_existing_event

        event = Event.parse_google_calendar_event(event_dict)
        assert event == mock_existing_event
        mock_filter.assert_called_once_with(key="12345")

    @patch("apps.owasp.models.event.Event.objects.filter")
    def test_parse_google_calendar_events(self, mock_filter):
        """Test the parsing of multiple Google Calendar events."""
        events_list = [
            {
                "id": "12345",
                "summary": "Event One",
                "start": {
                    "dateTime": "2025-05-26T09:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": "2025-05-30T17:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "status": "confirmed",
            },
            {
                "id": "67890",
                "summary": "Event Two",
                "end": {
                    "dateTime": "2025-06-12T15:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "status": "confirmed",
            },
            {
                "id": "67390",
                "summary": "Event Two",
                "start": {
                    "dateTime": "2025-06-10T10:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": "2025-06-12T15:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "status": "cancelled",
            },
        ]

        mock_filter.return_value.first.return_value = None

        events = Event.parse_google_calendar_events(events_list)
        assert len(events) == 1
        assert events[0].name == "Event One"

    def test_parse_non_confirmed_google_calendar_events(self):
        """Test the parsing of non-confirmed Google Calendar events."""
        events_list = [
            {
                "id": "12345",
                "summary": "Non-Confirmed Event",
                "start": {
                    "dateTime": "2025-05-26T09:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "end": {
                    "dateTime": "2025-05-30T17:00:00-07:00",
                    "timeZone": "America/Los_Angeles",
                },
                "status": "tentative",
            }
        ]
        events = Event.parse_google_calendar_events(events_list)
        assert len(events) == 0

    def test_from_dict(self):
        """Test the from_dict method with example data."""
        event = Event(key="test-event")
        category = "Global"
        data = {
            "name": "Example Global Event 2025",
            "start-date": "2025-05-26",
            "dates": "May 26-30, 2025",
            "optional-text": "This is a test description",
            "url": "https://example.com/event/global-event-2025",
        }

        with (
            patch("apps.owasp.models.event.Event.parse_dates") as mock_parse_dates,
            patch("apps.owasp.models.event.parser.parse") as mock_parser,
            patch("apps.owasp.models.event.normalize_url") as mock_normalize_url,
        ):
            mock_parse_dates.return_value = date(2025, 5, 30)
            mock_date = Mock()
            mock_date.date.return_value = date(2025, 5, 26)
            mock_parser.return_value = mock_date
            mock_normalize_url.return_value = "https://example.com/event/global-event-2025"

            event.from_dict(category, data)

            assert event.category == Event.Category.GLOBAL
            assert event.name == "Example Global Event 2025"
            assert event.start_date == date(2025, 5, 26)
            assert event.end_date == date(2025, 5, 30)
            assert event.description == "This is a test description"
            assert event.url == "https://example.com/event/global-event-2025"

    @pytest.mark.parametrize(
        ("category_str", "expected_category"),
        [
            ("Global", Event.Category.GLOBAL),
            ("AppSec Days", Event.Category.APPSEC_DAYS),
            ("Partner", Event.Category.PARTNER),
            ("Unknown", Event.Category.OTHER),
        ],
    )
    def test_category_mapping(self, category_str, expected_category):
        """Test that category strings are correctly mapped to enum values."""
        event = Event(key="test-event")
        data = {
            "name": "Example Event",
            "start-date": date(2025, 1, 1),
            "dates": "",
        }

        with (
            patch("apps.owasp.models.event.Event.parse_dates") as mock_parse_dates,
            patch("apps.owasp.models.event.normalize_url") as mock_normalize_url,
        ):
            mock_parse_dates.return_value = None
            mock_normalize_url.return_value = ""
            event.from_dict(category_str, data)
            assert event.category == expected_category
