from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest

from apps.api.rest.v0.event import EventDetail, get_event, list_events


@pytest.mark.parametrize(
    "event_data",
    [
        {
            "key": "test-event",
            "name": "Test Event",
            "description": "A test event",
            "url": "https://github.com/owasp/Nest",
            "end_date": "2025-03-14T00:00:00Z",
            "start_date": "2025-03-14T00:00:00Z",
        },
        {
            "key": "biggest-event",
            "name": "biggest event",
            "description": "this is a biggest event",
            "url": "https://github.com/owasp",
            "end_date": "2023-05-18T00:00:00Z",
            "start_date": "2022-05-19T00:00:00Z",
        },
    ],
)
def test_event_serializer_validation(event_data):
    event = EventDetail(**event_data)

    assert event.description == event_data["description"]
    assert event.end_date == datetime.fromisoformat(event_data["end_date"])
    assert event.key == event_data["key"]
    assert event.name == event_data["name"]
    assert event.start_date == datetime.fromisoformat(event_data["start_date"])
    assert event.url == event_data["url"]


class TestListEvents:
    """Test cases for list_events endpoint."""

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_list_events_with_ordering(self, mock_objects):
        """Test listing events with custom ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_objects.order_by.return_value = mock_queryset

        result = list_events(mock_request, ordering="start_date")

        mock_objects.order_by.assert_called_once_with("start_date", "-end_date", "id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_list_events_with_default_ordering(self, mock_objects):
        """Test that None ordering triggers default '-start_date' ordering."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_objects.order_by.return_value = mock_queryset

        result = list_events(mock_request, ordering=None)

        mock_objects.order_by.assert_called_once_with("-start_date", "-end_date", "id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_list_events_ordering_by_end_date(self, mock_objects):
        """Test listing events with ordering by end_date uses start_date as secondary."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_objects.order_by.return_value = mock_queryset

        result = list_events(mock_request, ordering="end_date")

        mock_objects.order_by.assert_called_once_with("end_date", "start_date", "id")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_list_events_ordering_by_negative_end_date(self, mock_objects):
        """Test listing events with ordering by -end_date uses -start_date as secondary."""
        mock_request = MagicMock()
        mock_queryset = MagicMock()

        mock_objects.order_by.return_value = mock_queryset

        result = list_events(mock_request, ordering="-end_date")

        mock_objects.order_by.assert_called_once_with("-end_date", "-start_date", "id")
        assert result == mock_queryset


class TestGetEvent:
    """Test cases for get_event endpoint."""

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_get_event_found(self, mock_objects):
        """Test getting an event that exists."""
        mock_request = MagicMock()
        mock_event = MagicMock()
        mock_filter = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_event

        result = get_event(mock_request, event_id="owasp-global-appsec-usa-2025")

        mock_objects.filter.assert_called_once_with(key__iexact="owasp-global-appsec-usa-2025")
        mock_filter.first.assert_called_once()
        assert result == mock_event

    @patch("apps.api.rest.v0.event.EventModel.objects")
    def test_get_event_not_found(self, mock_objects):
        """Test getting an event that does not exist returns 404."""
        mock_request = MagicMock()
        mock_filter = MagicMock()

        mock_objects.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = get_event(mock_request, event_id="nonexistent-event")

        mock_objects.filter.assert_called_once_with(key__iexact="nonexistent-event")
        mock_filter.first.assert_called_once()
        assert result.status_code == HTTPStatus.NOT_FOUND
        assert b"Event not found" in result.content
