"""Test cases for EventQuery."""

from unittest.mock import Mock, patch

from apps.owasp.api.internal.queries.event import EventQuery


class TestEventQuery:
    """Test cases for EventQuery class."""

    def test_event_query_has_strawberry_definition(self):
        """Test if EventQuery is a valid Strawberry type."""
        assert hasattr(EventQuery, "__strawberry_definition__")

        field_names = [field.name for field in EventQuery.__strawberry_definition__.fields]
        assert "upcoming_events" in field_names

    def test_upcoming_events_valid_limit(self):
        """Test upcoming_events with valid limit."""
        mock_events = [Mock(), Mock()]

        with patch("apps.owasp.models.event.Event.upcoming_events") as mock_upcoming:
            mock_upcoming.return_value.__getitem__ = Mock(return_value=mock_events)

            query = EventQuery()
            query.upcoming_events(limit=5)

            assert mock_upcoming.called

    def test_upcoming_events_invalid_limit(self):
        """Test upcoming_events with invalid limit returns empty list."""
        query = EventQuery()
        result = query.upcoming_events(limit=0)
        assert result == []
        result = query.upcoming_events(limit=-1)
        assert result == []
