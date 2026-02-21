from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.api.rest.v0.event import EventDetail, get_event, list_events
from apps.owasp.models.event import Event as EventModel

current_timezone = timezone.get_current_timezone()


class TestEventSerializerValidation:
    @pytest.mark.parametrize(
        "event_object",
        [
            EventModel(
                description="this is a sample event",
                end_date=datetime(2023, 6, 15, tzinfo=current_timezone).date(),
                key="sample-event",
                latitude=59.9139,
                longitude=10.7522,
                name="sample event",
                start_date=datetime(2023, 6, 14, tzinfo=current_timezone).date(),
                url="https://github.com/owasp/Nest",
            ),
            EventModel(
                description=None,
                end_date=None,
                key="event-without-end-date",
                latitude=None,
                longitude=None,
                name="event without end date",
                start_date=datetime(2023, 7, 1, tzinfo=current_timezone).date(),
                url=None,
            ),
        ],
    )
    def test_event_serializer_validation(self, event_object: EventModel):
        event = EventDetail.from_orm(event_object)

        assert event.description == event_object.description
        end_date = event_object.end_date.isoformat() if event_object.end_date else None
        assert event.end_date == end_date
        assert event.key == event_object.key
        assert event.latitude == event_object.latitude
        assert event.longitude == event_object.longitude
        assert event.name == event_object.name
        assert event.start_date == event_object.start_date.isoformat()
        assert event.url == event_object.url


class TestListEvents:
    """Tests for list_events endpoint."""

    @patch("apps.api.rest.v0.event.EventModel")
    def test_list_events_default(self, mock_event_model):
        """Test listing events with default ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_event_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_events(mock_request, mock_filters, ordering=None, is_upcoming=None)

        mock_event_model.objects.order_by.assert_called_with("-start_date", "-end_date")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.event.EventModel")
    def test_list_events_with_ordering(self, mock_event_model):
        """Test listing events with custom ordering."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_queryset = MagicMock()
        mock_event_model.objects.order_by.return_value = mock_queryset
        mock_filters.filter.return_value = mock_queryset

        result = list_events(mock_request, mock_filters, ordering="latitude", is_upcoming=None)

        mock_event_model.objects.order_by.assert_called_with("latitude", "-end_date")
        assert result == mock_queryset

    @patch("apps.api.rest.v0.event.EventModel")
    def test_list_events_upcoming(self, mock_event_model):
        """Test listing upcoming events."""
        mock_request = MagicMock()
        mock_filters = MagicMock()
        mock_upcoming_qs = MagicMock()
        mock_event_model.upcoming_events.return_value.order_by.return_value = mock_upcoming_qs
        mock_filters.filter.return_value = mock_upcoming_qs

        result = list_events(mock_request, mock_filters, ordering=None, is_upcoming=True)

        mock_event_model.upcoming_events.assert_called_once()
        assert result == mock_upcoming_qs


class TestGetEvent:
    """Tests for get_event endpoint."""

    @patch("apps.api.rest.v0.event.EventModel")
    def test_get_event_success(self, mock_event_model):
        """Test getting an event when found."""
        mock_request = MagicMock()
        mock_event = MagicMock()
        mock_event_model.objects.filter.return_value.first.return_value = mock_event

        result = get_event(mock_request, "sample-event")

        mock_event_model.objects.filter.assert_called_with(key__iexact="sample-event")
        assert result == mock_event

    @patch("apps.api.rest.v0.event.EventModel")
    def test_get_event_not_found(self, mock_event_model):
        """Test getting an event when not found."""
        mock_request = MagicMock()
        mock_event_model.objects.filter.return_value.first.return_value = None

        result = get_event(mock_request, "nonexistent-event")

        assert result.status_code == HTTPStatus.NOT_FOUND
