"""Test cases for Nest Calendar Events handlers."""

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.nest.handlers.calendar_events import get_calendar_id, schedule_reminder, set_reminder
from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.event import Event
from apps.slack.models.member import Member

MESSAGE = "Reminder Message"
USER_ID = "U123456"
EVENT_NUMBER = 1


class TestCalendarEventsHandlers:
    """Test cases for Nest Calendar Events handlers."""

    @patch("apps.nest.handlers.calendar_events.cache.get")
    def test_get_calendar_id_cache_hit(self, mock_cache_get):
        """Test get_calendar_id function when cache hit."""
        mock_cache_get.return_value = "calendar_id"
        result = get_calendar_id(USER_ID, EVENT_NUMBER)
        assert result == "calendar_id"
        mock_cache_get.assert_called_once_with(f"{USER_ID}_1")

    @patch("apps.nest.handlers.calendar_events.cache.get")
    def test_get_calendar_id_cache_miss(self, mock_cache_get):
        """Test get_calendar_id function when cache miss."""
        mock_cache_get.return_value = None
        with pytest.raises(ValidationError) as excinfo:
            get_calendar_id(USER_ID, EVENT_NUMBER)
        assert "Invalid or expired event number" in str(excinfo.value)
        mock_cache_get.assert_called_once_with(f"{USER_ID}_1")

    @patch("apps.nest.handlers.calendar_events.GoogleCalendarClient")
    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    @patch("apps.nest.handlers.calendar_events.Event.save")
    @patch("apps.nest.handlers.calendar_events.Reminder.objects.get_or_create")
    @patch("apps.nest.handlers.calendar_events.schedule_reminder")
    @patch("apps.nest.handlers.calendar_events.transaction.atomic")
    def test_set_reminder_success(
        self,
        mock_transaction_atomic,
        mock_schedule_reminder,
        mock_reminder_get_or_create,
        mock_event_save,
        mock_parse_event,
        mock_google_client,
    ):
        """Test setting a reminder successfully."""
        mock_transaction_atomic.return_value.__enter__.return_value = None
        mock_transaction_atomic.return_value.__exit__.return_value = None

        # Mock inputs
        mock_channel = MagicMock(spec=EntityChannel)
        mock_member = MagicMock(spec=Member)
        google_calendar_id = "google_calendar_event_id"
        minutes_before = 15
        recurrence = "daily"
        message = MESSAGE

        mock_event = Event(
            google_calendar_id="event_id",
            key="event_key",
            name="Test Event",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
            description="Event Description",
        )
        mock_parse_event.return_value = mock_event

        mock_reminder = MagicMock(spec=Reminder)
        mock_reminder_get_or_create.return_value = (mock_reminder, False)

        mock_schedule = MagicMock(spec=ReminderSchedule)
        mock_schedule_reminder.return_value = mock_schedule

        # Call the function
        result = set_reminder(
            channel=mock_channel,
            client=mock_google_client,
            member=mock_member,
            google_calendar_id=google_calendar_id,
            minutes_before=minutes_before,
            recurrence=recurrence,
            message=message,
        )

        # Assertions
        assert result == mock_schedule
        mock_parse_event.assert_called_once()
        mock_event_save.assert_called_once()
        mock_reminder_get_or_create.assert_called_once()
        mock_schedule_reminder.assert_called_once()

    def test_set_reminder_invalid_minutes_before(self):
        """Test setting a reminder with invalid minutes_before."""
        mock_channel = MagicMock(spec=EntityChannel)
        mock_client = MagicMock()
        mock_member = MagicMock(spec=Member)

        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel=mock_channel,
                client=mock_client,
                member=mock_member,
                google_calendar_id="calendar_id",
                minutes_before=0,
                recurrence="daily",
                message=MESSAGE,
            )
        assert "Minutes before must be a positive integer" in str(excinfo.value)

    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    def test_set_reminder_event_retrieval_failure(self, mock_parse_event):
        """Test setting a reminder when event retrieval fails."""
        mock_channel = MagicMock(spec=EntityChannel)
        mock_client = MagicMock()
        mock_member = MagicMock(spec=Member)

        mock_client.get_event.return_value = {"id": "event_id", "summary": "Test Event"}
        mock_parse_event.return_value = None

        with pytest.raises((ValidationError, ValueError)):
            set_reminder(
                channel=mock_channel,
                client=mock_client,
                member=mock_member,
                google_calendar_id="calendar_id",
                minutes_before=15,
                recurrence="daily",
                message=MESSAGE,
            )

    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    def test_set_reminder_past_reminder_time(self, mock_parse_event):
        """Test setting a reminder with a past reminder time."""
        mock_channel = MagicMock(spec=EntityChannel)
        mock_client = MagicMock()
        mock_member = MagicMock(spec=Member)

        mock_client.get_event.return_value = {"id": "event_id", "summary": "Test Event"}
        mock_event = Event(
            google_calendar_id="event_id",
            key="event_key",
            name="Test Event",
            start_date=timezone.now() + timezone.timedelta(minutes=10),
            end_date=timezone.now() + timezone.timedelta(hours=1),
            description="Event Description",
        )
        mock_parse_event.return_value = mock_event

        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel=mock_channel,
                client=mock_client,
                member=mock_member,
                google_calendar_id="calendar_id",
                minutes_before=15,  # More than 10 minutes, so reminder would be in the past
                recurrence="daily",
                message=MESSAGE,
            )
        assert "must be in the future" in str(excinfo.value)

    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    def test_set_reminder_invalid_recurrence(self, mock_parse_event):
        """Test setting a reminder with an invalid recurrence value."""
        mock_channel = MagicMock(spec=EntityChannel)
        mock_client = MagicMock()
        mock_member = MagicMock(spec=Member)

        mock_client.get_event.return_value = {"id": "event_id", "summary": "Test Event"}
        mock_event = Event(
            google_calendar_id="event_id",
            key="event_key",
            name="Test Event",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
            description="Event Description",
        )
        mock_parse_event.return_value = mock_event

        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel=mock_channel,
                client=mock_client,
                member=mock_member,
                google_calendar_id="calendar_id",
                minutes_before=15,
                recurrence="invalid_recurrence",
                message=MESSAGE,
            )
        assert "Invalid recurrence" in str(excinfo.value)

    @patch("apps.nest.handlers.calendar_events.ReminderSchedule.objects.create")
    def test_schedule_reminder_success(self, mock_reminder_create):
        """Test scheduling a reminder successfully."""
        # Mock inputs
        mock_entity_channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=Member(slack_user_id="U123456"),
            event=Event(
                google_calendar_id="event_id",
                key="event_key",
                name="Test Event",
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
                description="Event Description",
            ),
            message="Test Reminder",
            entity_channel=mock_entity_channel,
        )
        scheduled_time = timezone.now() + timezone.timedelta(hours=1)
        recurrence = "weekly"

        # Mock return value
        mock_reminder_schedule = ReminderSchedule(
            reminder=reminder,
            scheduled_time=scheduled_time,
            recurrence=recurrence,
        )
        mock_reminder_create.return_value = mock_reminder_schedule

        # Call the function
        result = schedule_reminder(reminder, scheduled_time, recurrence)

        # Assertions
        assert result == mock_reminder_schedule
        mock_reminder_create.assert_called_once_with(
            reminder=reminder,
            scheduled_time=scheduled_time,
            recurrence=recurrence,
        )

    def test_schedule_reminder_past_time(self):
        """Test scheduling a reminder with a past scheduled time."""
        mock_entity_channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=Member(slack_user_id="U123456"),
            event=Event(
                google_calendar_id="event_id",
                key="event_key",
                name="Test Event",
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
                description="Event Description",
            ),
            message="Test Reminder",
            entity_channel=mock_entity_channel,
        )
        past_time = timezone.now() - timezone.timedelta(hours=1)

        with pytest.raises(ValidationError) as excinfo:
            schedule_reminder(reminder, past_time, "daily")
        assert "must be in the future" in str(excinfo.value)

    def test_schedule_reminder_invalid_recurrence(self):
        """Test scheduling a reminder with an invalid recurrence value."""
        mock_entity_channel = EntityChannel(channel_id=5)
        reminder = Reminder(
            member=Member(slack_user_id="U123456"),
            event=Event(
                google_calendar_id="event_id",
                key="event_key",
                name="Test Event",
                start_date=timezone.now() + timezone.timedelta(days=1),
                end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
                description="Event Description",
            ),
            message="Test Reminder",
            entity_channel=mock_entity_channel,
        )

        with pytest.raises(ValidationError) as excinfo:
            schedule_reminder(
                reminder, timezone.now() + timezone.timedelta(hours=1), "invalid_recurrence"
            )
        assert "Invalid recurrence" in str(excinfo.value)
