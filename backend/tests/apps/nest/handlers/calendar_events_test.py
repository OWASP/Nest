"""Test cases for Nest Calendar Events handlers."""

from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.nest.handlers.calendar_events import schedule_reminder, set_reminder
from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.event import Event
from apps.slack.models.member import Member

MESSAGE = "Reminder Message"


class TestCalendarEventsHandlers:
    """Test cases for Nest Calendar Events handlers."""

    @patch("apps.nest.handlers.calendar_events.GoogleCalendarClient")
    @patch("apps.nest.handlers.calendar_events.cache")
    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    @patch("apps.nest.handlers.calendar_events.Event.save")
    @patch("apps.nest.handlers.calendar_events.Member.objects.get")
    @patch("apps.nest.handlers.calendar_events.Reminder.objects.create")
    @patch("apps.nest.handlers.calendar_events.schedule_reminder")
    def test_set_reminder_success(
        self,
        mock_schedule_reminder,
        mock_reminder_create,
        mock_member_get,
        mock_event_save,
        mock_parse_event,
        mock_authorize,
        mock_cache,
        mock_google_client,
    ):
        """Test setting a reminder successfully."""
        # Mock inputs
        channel = "C123456"
        event_number = "1"
        user_id = "U123456"
        minutes_before = 15
        recurrence = "daily"
        message = MESSAGE

        # Mock return values
        mock_member = Member(slack_user_id=user_id)
        mock_member_get.return_value = mock_member
        mock_auth = GoogleAccountAuthorization(
            access_token="access_token",  # noqa: S106
            refresh_token="refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_authorize.return_value = mock_auth
        mock_cache.get.return_value = "google_calendar_event_id"
        mock_event = Event(
            google_calendar_id="event_id",
            key="event_key",
            name="Test Event",
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1, hours=1),
            description="Event Description",
        )
        mock_parse_event.return_value = mock_event
        mock_reminder = Reminder(
            member=mock_member,
            event=mock_event,
            message=message,
            channel_id=channel,
        )
        mock_reminder_create.return_value = mock_reminder
        mock_schedule_reminder.return_value = ReminderSchedule(
            reminder=mock_reminder,
            scheduled_time=mock_event.start_date - timezone.timedelta(minutes=minutes_before),
            recurrence=recurrence,
        )

        # Call the function
        result = set_reminder(
            channel=channel,
            event_number=event_number,
            user_id=user_id,
            minutes_before=minutes_before,
            recurrence=recurrence,
            message=message,
        )
        # Assertions
        assert result.reminder.member == mock_member
        assert result.reminder.event == mock_event
        assert result.recurrence == recurrence
        mock_member_get.assert_called_once_with(slack_user_id=user_id)
        mock_authorize.assert_called_once_with(user_id)
        mock_cache.get.assert_called_once_with(f"{user_id}_{event_number}")
        mock_parse_event.assert_called_once()
        mock_event_save.assert_called_once()
        mock_google_client.assert_called_once_with(mock_auth)

    def test_set_reminder_invalid_minutes_before(self):
        """Test setting a reminder with invalid minutes_before."""
        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel="C123456",
                event_number="1",
                user_id="U123456",
                minutes_before=0,
                recurrence="daily",
                message=MESSAGE,
            )
        assert excinfo.value.message == "Minutes before must be a positive integer."

    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    def test_set_reminder_unauthorized_user(self, mock_authorize):
        """Test setting a reminder with an unauthorized user."""
        mock_authorize.return_value = ("http://auth.url", "state")  # NOSONAR
        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel="C123456",
                event_number="1",
                user_id="U123456",
                minutes_before=15,
                recurrence="daily",
                message=MESSAGE,
            )
        assert excinfo.value.message == "User is not authorized with Google. Please sign in first."
        mock_authorize.assert_called_once_with("U123456")

    @patch("apps.nest.handlers.calendar_events.cache")
    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    def test_set_reminder_invalid_event_number(self, mock_authorize, mock_cache):
        """Test setting a reminder with an invalid event number."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="access_token",  # noqa: S106
            refresh_token="refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_cache.get.return_value = None
        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel="C123456",
                event_number="invalid_event_number",
                user_id="U123456",
                minutes_before=15,
                recurrence="daily",
                message=MESSAGE,
            )
        assert excinfo.value.message == (
            "Invalid or expired event number. Please get a new event number from the events list."
        )
        mock_authorize.assert_called_once_with("U123456")
        mock_cache.get.assert_called_once_with("U123456_invalid_event_number")

    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    @patch("apps.nest.handlers.calendar_events.cache")
    @patch("apps.nest.handlers.calendar_events.GoogleCalendarClient")
    def test_set_reminder_event_retrieval_failure(
        self,
        mock_google_client,
        mock_cache,
        mock_parse_event,
        mock_authorize,
    ):
        """Test setting a reminder when event retrieval fails."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="access_token",  # noqa: S106
            refresh_token="refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_cache.get.return_value = "google_calendar_event_id"
        mock_parse_event.return_value = None
        with pytest.raises(ValidationError) as excinfo:
            set_reminder(
                channel="C123456",
                event_number="1",
                user_id="U123456",
                minutes_before=15,
                recurrence="daily",
                message=MESSAGE,
            )
        assert (
            excinfo.value.message
            == "Could not retrieve the event details. Please try again later."
        )
        mock_authorize.assert_called_once_with("U123456")
        mock_cache.get.assert_called_once_with("U123456_1")
        mock_parse_event.assert_called_once()
        mock_google_client.assert_called_once()

    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    @patch("apps.nest.handlers.calendar_events.cache")
    @patch("apps.nest.handlers.calendar_events.GoogleCalendarClient")
    def test_set_reminder_past_reminder_time(
        self,
        mock_google_client,
        mock_cache,
        mock_parse_event,
        mock_authorize,
    ):
        """Test setting a reminder with a past reminder time."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="access_token",  # noqa: S106
            refresh_token="refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_cache.get.return_value = "google_calendar_event_id"
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
                channel="C123456",
                event_number="1",
                user_id="U123456",
                minutes_before=15,
                recurrence="daily",
                message=MESSAGE,
            )
        assert (
            excinfo.value.message
            == "Reminder time must be in the future. Please adjust the minutes before."
        )
        mock_authorize.assert_called_once_with("U123456")
        mock_cache.get.assert_called_once_with("U123456_1")
        mock_parse_event.assert_called_once()
        mock_google_client.assert_called_once()

    @patch("apps.nest.handlers.calendar_events.GoogleAccountAuthorization.authorize")
    @patch("apps.nest.handlers.calendar_events.Event.parse_google_calendar_event")
    @patch("apps.nest.handlers.calendar_events.cache")
    @patch("apps.nest.handlers.calendar_events.GoogleCalendarClient")
    def test_set_reminder_invalid_recurrence(
        self,
        mock_google_client,
        mock_cache,
        mock_parse_event,
        mock_authorize,
    ):
        """Test setting a reminder with an invalid recurrence value."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="access_token",  # noqa: S106
            refresh_token="refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_cache.get.return_value = "google_calendar_event_id"
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
                channel="C123456",
                event_number="1",
                user_id="U123456",
                minutes_before=15,
                recurrence="invalid_recurrence",
                message=MESSAGE,
            )
        assert excinfo.value.message == "Invalid recurrence value."
        mock_authorize.assert_called_once_with("U123456")
        mock_cache.get.assert_called_once_with("U123456_1")
        mock_parse_event.assert_called_once()
        mock_google_client.assert_called_once()

    @patch("apps.nest.handlers.calendar_events.ReminderSchedule.objects.create")
    def test_schedule_reminder_success(self, mock_reminder_create):
        """Test scheduling a reminder successfully."""
        # Mock inputs
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
            channel_id="C123456",
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
            channel_id="C123456",
        )
        past_time = timezone.now() - timezone.timedelta(hours=1)
        with pytest.raises(ValidationError) as excinfo:
            schedule_reminder(reminder, past_time, "daily")
        assert excinfo.value.message == "Scheduled time must be in the future."

    def test_schedule_reminder_invalid_recurrence(self):
        """Test scheduling a reminder with an invalid recurrence value."""
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
            channel_id="C123456",
        )
        with pytest.raises(ValidationError) as excinfo:
            schedule_reminder(
                reminder, timezone.now() + timezone.timedelta(hours=1), "invalid_recurrence"
            )
        assert excinfo.value.message == "Invalid recurrence value."
