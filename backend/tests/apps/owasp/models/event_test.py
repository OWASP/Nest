import math
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

    def test_parse_dates_iso_format_invalid(self):
        """Test parse_dates with invalid ISO-like single date returns None."""
        result = Event.parse_dates("0000-00-00", date(2025, 5, 26))
        assert result is None

    def test_parse_dates_year_crossover(self):
        """Test parse_dates with year crossover when end month is before start month."""
        result = Event.parse_dates("December 25 - January 5", date(2025, 12, 25))
        assert result == date(2026, 1, 5)

    def test_parse_dates_no_year_crossover(self):
        """Test parse_dates without year crossover when end is after start."""
        result = Event.parse_dates("May 1 - May 5", date(2025, 5, 1))
        assert result == date(2025, 5, 5)

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


class TestEventUpcomingEvents:
    """Test cases for upcoming_events static method."""

    def test_upcoming_events(self):
        """Test upcoming_events returns future events."""
        with patch.object(Event, "objects") as mock_objects:
            mock_qs = Mock()
            mock_objects.filter.return_value.exclude.return_value.order_by.return_value = mock_qs

            result = Event.upcoming_events()

            assert result == mock_qs
            mock_objects.filter.assert_called_once()


class TestEventUpdateData:
    """Test cases for update_data method."""

    def test_update_data_new_event(self):
        """Test update_data creates new event when not found."""
        category = "Global"
        data = {
            "name": "New Event",
            "start-date": date(2025, 5, 26),
            "dates": "May 26-30, 2025",
        }

        with (
            patch("apps.owasp.models.event.slugify") as mock_slugify,
            patch("apps.owasp.models.event.Event.objects.get") as mock_get,
            patch.object(Event, "from_dict") as mock_from_dict,
            patch.object(Event, "save") as mock_save,
        ):
            mock_slugify.return_value = "new-event"
            mock_get.side_effect = Event.DoesNotExist

            result = Event.update_data(category, data)

            assert result is not None
            mock_from_dict.assert_called_once()
            mock_save.assert_called_once()

    def test_update_data_keyerror_returns_none(self):
        """Test update_data returns None on KeyError from from_dict."""
        category = "Global"
        data = {"name": "Test Event", "start-date": date(2025, 5, 26)}

        with (
            patch("apps.owasp.models.event.slugify") as mock_slugify,
            patch("apps.owasp.models.event.Event.objects.get") as mock_get,
            patch.object(Event, "from_dict") as mock_from_dict,
        ):
            mock_slugify.return_value = "test-event"
            mock_get.side_effect = Event.DoesNotExist
            mock_from_dict.side_effect = KeyError("missing-key")

            result = Event.update_data(category, data)

            assert result is None


class TestEventGeoMethods:
    """Test cases for geo-related methods."""

    def test_generate_geo_location_with_suggested_location(self):
        """Test generate_geo_location uses suggested_location."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="San Francisco, CA",
        )
        mock_location = Mock()
        mock_location.latitude = 37.7749
        mock_location.longitude = -122.4194

        with patch("apps.owasp.models.event.get_location_coordinates") as mock_get_coords:
            mock_get_coords.return_value = mock_location

            event.generate_geo_location()

            assert math.isclose(event.latitude, 37.7749)
            assert math.isclose(event.longitude, -122.4194)
            mock_get_coords.assert_called_once_with("San Francisco, CA")

    def test_generate_geo_location_falls_back_to_context(self):
        """Test generate_geo_location falls back to context when suggested_location fails."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="",
        )
        mock_location = Mock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060

        with patch("apps.owasp.models.event.get_location_coordinates") as mock_get_coords:
            mock_get_coords.return_value = mock_location

            event.generate_geo_location()

            assert math.isclose(event.latitude, 40.7128)
            assert math.isclose(event.longitude, -74.0060)

    def test_generate_geo_location_both_return_none(self):
        """Test generate_geo_location does not set lat/long when both lookups fail."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="Unknown Place",
            latitude=None,
            longitude=None,
        )

        with patch("apps.owasp.models.event.get_location_coordinates") as mock_get_coords:
            mock_get_coords.return_value = None

            event.generate_geo_location()

            assert event.latitude is None
            assert event.longitude is None

    def test_generate_geo_location_suggested_is_none_string(self):
        """Test generate_geo_location skips suggested_location when it equals 'None'."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="None",
        )
        mock_location = Mock()
        mock_location.latitude = 51.5074
        mock_location.longitude = -0.1278

        with patch("apps.owasp.models.event.get_location_coordinates") as mock_get_coords:
            mock_get_coords.return_value = mock_location

            event.generate_geo_location()

            # Should skip "None" and use context instead
            assert math.isclose(event.latitude, 51.5074)
            assert math.isclose(event.longitude, -0.1278)

    def test_generate_suggested_location(self):
        """Test generate_suggested_location uses OpenAI."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
        )

        with (
            patch("apps.owasp.models.event.OpenAi") as mock_openai_cls,
            patch("apps.owasp.models.event.Prompt") as mock_prompt,
        ):
            mock_openai = Mock()
            mock_openai_cls.return_value = mock_openai
            mock_openai.set_input.return_value = mock_openai
            mock_openai.set_max_tokens.return_value = mock_openai
            mock_openai.set_prompt.return_value = mock_openai
            mock_openai.complete.return_value = "New York, NY"
            mock_prompt.get_owasp_event_suggested_location.return_value = "prompt"

            event.generate_suggested_location()

            assert event.suggested_location == "New York, NY"

    def test_generate_suggested_location_handles_none_result(self):
        """Test generate_suggested_location handles None result."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
        )

        with (
            patch("apps.owasp.models.event.OpenAi") as mock_openai_cls,
            patch("apps.owasp.models.event.Prompt"),
        ):
            mock_openai = Mock()
            mock_openai_cls.return_value = mock_openai
            mock_openai.set_input.return_value = mock_openai
            mock_openai.set_max_tokens.return_value = mock_openai
            mock_openai.set_prompt.return_value = mock_openai
            mock_openai.complete.return_value = "None"

            event.generate_suggested_location()

            assert event.suggested_location == ""

    def test_generate_suggested_location_handles_exception(self):
        """Test generate_suggested_location handles exceptions."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
        )

        with (
            patch("apps.owasp.models.event.OpenAi") as mock_openai_cls,
            patch("apps.owasp.models.event.Prompt"),
        ):
            mock_openai = Mock()
            mock_openai_cls.return_value = mock_openai
            mock_openai.set_input.return_value = mock_openai
            mock_openai.set_max_tokens.return_value = mock_openai
            mock_openai.set_prompt.return_value = mock_openai
            mock_openai.complete.side_effect = ValueError("Error")

            event.generate_suggested_location()

            assert event.suggested_location == ""


class TestEventSummaryAndContext:
    """Test cases for generate_summary and get_context methods."""

    def test_generate_summary(self):
        """Test generate_summary uses OpenAI."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
        )

        with (
            patch("apps.owasp.models.event.OpenAi") as mock_openai_cls,
            patch("apps.owasp.models.event.Prompt") as mock_prompt,
        ):
            mock_openai = Mock()
            mock_openai_cls.return_value = mock_openai
            mock_openai.set_input.return_value = mock_openai
            mock_openai.set_max_tokens.return_value = mock_openai
            mock_openai.set_prompt.return_value = mock_openai
            mock_openai.complete.return_value = "A great event summary"
            mock_prompt.get_owasp_event_summary.return_value = "prompt"

            event.generate_summary()

            assert event.summary == "A great event summary"

    def test_generate_summary_handles_exception(self):
        """Test generate_summary handles exceptions."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
        )

        with (
            patch("apps.owasp.models.event.OpenAi") as mock_openai_cls,
            patch("apps.owasp.models.event.Prompt"),
        ):
            mock_openai = Mock()
            mock_openai_cls.return_value = mock_openai
            mock_openai.set_input.return_value = mock_openai
            mock_openai.set_max_tokens.return_value = mock_openai
            mock_openai.set_prompt.return_value = mock_openai
            mock_openai.complete.side_effect = TypeError("Error")

            event.generate_summary()

            assert event.summary == ""

    def test_get_context_without_dates(self):
        """Test get_context without dates."""
        event = Event(
            key="test-event",
            name="Test Event",
            description="Test description",
            summary="Test summary",
            start_date=date(2025, 1, 1),
        )

        result = event.get_context()

        assert "Name: Test Event" in result
        assert "Description: Test description" in result
        assert "Summary: Test summary" in result
        assert "Dates:" not in result

    def test_get_context_with_dates(self):
        """Test get_context with dates."""
        event = Event(
            key="test-event",
            name="Test Event",
            description="Test description",
            summary="Test summary",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 5),
        )

        result = event.get_context(include_dates=True)

        assert "Name: Test Event" in result
        assert "Dates:" in result


class TestEventSave:
    """Test cases for save method."""

    def test_save_generates_location_when_missing(self):
        """Test save generates suggested_location when empty."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="",
        )

        with (
            patch.object(Event, "generate_suggested_location") as mock_gen_location,
            patch.object(Event, "generate_geo_location") as mock_gen_geo,
            patch("apps.owasp.models.event.BulkSaveModel.save"),
            patch("apps.owasp.models.event.TimestampedModel.save"),
        ):
            event.save()

            mock_gen_location.assert_called_once()
            mock_gen_geo.assert_called_once()

    def test_save_generates_geo_when_missing(self):
        """Test save generates geo location when lat/long missing."""
        event = Event(
            key="test-event",
            name="Test Event",
            start_date=date(2025, 1, 1),
            suggested_location="New York",
            latitude=None,
            longitude=None,
        )

        with (
            patch.object(Event, "generate_geo_location") as mock_gen_geo,
            patch("apps.owasp.models.event.BulkSaveModel.save"),
            patch("apps.owasp.models.event.TimestampedModel.save"),
        ):
            event.save()

            mock_gen_geo.assert_called_once()

    @patch("apps.owasp.models.event.Event.generate_suggested_location")
    def test_save_does_not_call_geo_location_on_zero_coords(self, mock_suggested):
        """Verify 0.0 coordinates are treated as valid data."""
        event = Event(latitude=0.0, longitude=0.0, name="Test event")
        with (
            patch.object(event, "generate_geo_location") as mock_geo,
            patch.object(Event, "save_base"),
        ):
            event.save()
        mock_geo.assert_not_called()
