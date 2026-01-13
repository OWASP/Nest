from datetime import date
from unittest.mock import Mock, patch

import pytest

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
            (None, date(2025, 5, 26), None),
            ("", date(2025, 5, 26), None),
            ("May 26-30, 2025", date(2025, 5, 26), date(2025, 5, 30)),
            ("Invalid date range", date(2025, 5, 26), None),
        ],
    )
    def test_parse_dates_unit(self, dates, start_date, expected_result):
        """Unit test for parse_dates structure using mocks."""
        if not dates:
            assert Event.parse_dates(dates, start_date) is None
            return

        with patch("apps.owasp.models.event.parser.parse") as mock_parse:
            if expected_result:
                mock_date = Mock()
                mock_date.date.return_value = expected_result
                mock_parse.return_value = mock_date
                result = Event.parse_dates(dates, start_date)
                assert result == expected_result
            else:
                mock_parse.side_effect = ValueError("Invalid")
                result = Event.parse_dates(dates, start_date)
                assert result is None

    @pytest.mark.parametrize(
        ("dates", "start_date", "expected_result"),
        [
            ("2025-05-26", date(2025, 5, 26), date(2025, 5, 26)),
            ("Dec 30, 2025 - Jan 2, 2026", date(2025, 12, 30), date(2026, 1, 2)),
            ("June 5, 2025", date(2025, 6, 5), date(2025, 6, 5)),
            ("May 26-30, 2025", date(2025, 5, 26), date(2025, 5, 30)),
            ("May 26-30", date(2025, 5, 26), date(2025, 5, 30)),
            ("May 26–30, 2025", date(2025, 5, 26), date(2025, 5, 30)),  # noqa: RUF001
            ("May 26—30, 2025", date(2025, 5, 26), date(2025, 5, 30)),
            ("May 30 - June 2, 2025", date(2025, 5, 30), date(2025, 6, 2)),
        ],
    )
    def test_parse_dates_integration(self, dates, start_date, expected_result):
        """Test parse_dates with real parser to verify crossover and dash logic."""
        result = Event.parse_dates(dates, start_date)
        assert result == expected_result

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
            assert result == mock_event

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
            assert event.end_date == date(2025, 5, 30)

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
            "dates": "",
            "name": "Example Event",
            "start-date": date(2025, 1, 1),
        }
        with (
            patch("apps.owasp.models.event.Event.parse_dates") as mock_parse_dates,
            patch("apps.owasp.models.event.normalize_url") as mock_normalize_url,
        ):
            mock_parse_dates.return_value = None
            mock_normalize_url.return_value = ""
            event.from_dict(category_str, data)
            assert event.category == expected_category
