"""Test cases for slack calendar events handlers."""

from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import override_settings
from django.utils import timezone
from httplib2.error import ServerNotFoundError

from apps.nest.models.google_account_authorization import GoogleAccountAuthorization
from apps.nest.models.reminder import Reminder
from apps.nest.models.reminder_schedule import ReminderSchedule
from apps.owasp.models.event import Event
from apps.slack.common.handlers.calendar_events import (
    get_events_blocks,
    get_reminders_blocks,
    get_setting_reminder_blocks,
)
from apps.slack.common.presentation import EntityPresentation
from apps.slack.models.member import Member


class TestCalendarEvents:
    """Slack calendar events handlers test cases."""

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.GoogleCalendarClient")
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    @patch("apps.owasp.models.event.Event.parse_google_calendar_events")
    def test_get_events_blocks(
        self, mock_parse_events, mock_authorize, mock_google_calendar_client
    ):
        """Test get_events_blocks function."""
        auth = GoogleAccountAuthorization(
            access_token="test_access_token",  # noqa: S106
            refresh_token="test_refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_authorize.return_value = auth
        mock_google_calendar_client.return_value.get_events.return_value = [
            {
                "id": "event1",
                "summary": "Test Event 1",
                "start": {"dateTime": (timezone.now() + timezone.timedelta(hours=1)).isoformat()},
                "end": {"dateTime": (timezone.now() + timezone.timedelta(hours=2)).isoformat()},
                "status": "confirmed",
            },
            {
                "id": "event2",
                "summary": "Test Event 2",
                "start": {"dateTime": (timezone.now() + timezone.timedelta(hours=3)).isoformat()},
                "end": {"dateTime": (timezone.now() + timezone.timedelta(hours=4)).isoformat()},
                "status": "confirmed",
            },
        ]
        mock_parse_events.return_value = [
            Event(
                name="Test Event 1",
                start_date=timezone.now() + timezone.timedelta(hours=1),
                end_date=timezone.now() + timezone.timedelta(hours=2),
                google_calendar_id="event1",
                key="event1",
            ),
            Event(
                name="Test Event 2",
                start_date=timezone.now() + timezone.timedelta(hours=3),
                end_date=timezone.now() + timezone.timedelta(hours=4),
                google_calendar_id="event2",
                key="event2",
            ),
        ]
        blocks = get_events_blocks(
            "test_slack_user_id", presentation=EntityPresentation(include_pagination=True), page=1
        )
        assert len(blocks) == 4  # 1 header + 2 events + 1 pagination
        assert "*Your upcoming calendar events" in blocks[0]["text"]["text"]
        assert "Test Event 1" in blocks[1]["text"]["text"]
        assert "Test Event 2" in blocks[2]["text"]["text"]
        assert blocks[3]["type"] == "actions"
        mock_google_calendar_client.assert_called_once_with(auth)
        mock_google_calendar_client.return_value.get_events.assert_called_once()

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    def test_get_events_blocks_no_auth(self, mock_authorize):
        """Test get_events_blocks function when no authorization."""
        mock_authorize.return_value = ("http://auth.url", "state123")  # NOSONAR
        blocks = get_events_blocks(
            "test_slack_user_id", presentation=EntityPresentation(include_pagination=True), page=1
        )
        assert len(blocks) == 1
        assert (
            "*Please sign in with Google first through this <http://auth.url|link>*"
            in blocks[0]["text"]["text"]
        )

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.GoogleCalendarClient")
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    def test_get_events_blocks_service_error(self, mock_authorize, mock_google_calendar_client):
        """Test get_events_blocks function when Google Calendar service error."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="test_access_token",  # noqa: S106
            refresh_token="test_refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_google_calendar_client.side_effect = ServerNotFoundError()
        blocks = get_events_blocks(
            "test_slack_user_id", presentation=EntityPresentation(include_pagination=True), page=1
        )
        assert len(blocks) == 1
        assert "*Please check your internet connection.*" in blocks[0]["text"]["text"]

    @override_settings(IS_GOOGLE_AUTH_ENABLED=True, IS_AWS_KMS_ENABLED=True)
    @patch("apps.nest.clients.google_calendar.GoogleCalendarClient")
    @patch("apps.nest.models.google_account_authorization.GoogleAccountAuthorization.authorize")
    def test_get_events_blocks_no_events(self, mock_authorize, mock_google_calendar_client):
        """Test get_events_blocks function when no events."""
        mock_authorize.return_value = GoogleAccountAuthorization(
            access_token="test_access_token",  # noqa: S106
            refresh_token="test_refresh_token",  # noqa: S106
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        mock_google_calendar_client.return_value.get_events.return_value = []
        blocks = get_events_blocks(
            "test_slack_user_id", presentation=EntityPresentation(include_pagination=True), page=1
        )
        assert len(blocks) == 1
        assert "*No upcoming calendar events found.*" in blocks[0]["text"]["text"]

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.filter")
    def test_get_reminders_blocks_success(self, mock_filter):
        """Test get_reminders_blocks function."""
        mock_filter.return_value.order_by.return_value = [
            MagicMock(
                spec=ReminderSchedule,
                pk=1,
                reminder=MagicMock(
                    spec=Reminder,
                    channel_id="C123456",
                    message="Test reminder message",
                ),
                scheduled_time=timezone.now() + timezone.timedelta(minutes=10),
                recurrence="once",
            ),
            MagicMock(
                spec=ReminderSchedule,
                pk=2,
                reminder=MagicMock(
                    spec=Reminder,
                    channel_id="C654321",
                    message="Another reminder message",
                ),
                scheduled_time=timezone.now() + timezone.timedelta(minutes=20),
                recurrence="daily",
            ),
        ]
        blocks = get_reminders_blocks("test_slack_user_id")
        assert len(blocks) == 3  # 1 header + 2 reminders
        assert "*Your upcoming reminders:*" in blocks[0]["text"]["text"]
        assert "Test reminder message" in blocks[1]["text"]["text"]
        assert "Another reminder message" in blocks[2]["text"]["text"]
        mock_filter.assert_called_once_with(reminder__member__slack_user_id="test_slack_user_id")
        mock_filter.return_value.order_by.assert_called_once_with("scheduled_time")

    @patch("apps.nest.models.reminder_schedule.ReminderSchedule.objects.filter")
    def test_get_reminders_blocks_no_reminders(self, mock_filter):
        """Test get_reminders_blocks function when no reminders."""
        mock_filter.return_value.order_by.return_value = []
        blocks = get_reminders_blocks("test_slack_user_id")
        assert len(blocks) == 1
        assert (
            "*No reminders found. You can set one with `/nestbot reminder set`*"
            in blocks[0]["text"]["text"]
        )
        mock_filter.assert_called_once_with(reminder__member__slack_user_id="test_slack_user_id")
        mock_filter.return_value.order_by.assert_called_once_with("scheduled_time")

    @patch("apps.nest.handlers.calendar_events.set_reminder")
    @patch("apps.nest.schedulers.calendar_events.slack.SlackScheduler")
    def test_get_setting_reminder_blocks_success(self, mock_slack_scheduler, mock_set_reminder):
        """Test get_setting_reminder_blocks function for successful reminder setting."""
        mock_set_reminder.return_value = MagicMock(
            spec=ReminderSchedule,
            reminder=MagicMock(
                spec=Reminder,
                channel_id="C123456",
                message="Test reminder message",
                member=MagicMock(slack_user_id="test_slack_user_id", spec=Member),
                event=MagicMock(spec=Event, name="Test Event"),
            ),
            scheduled_time=timezone.now() + timezone.timedelta(minutes=10),
            recurrence="daily",
        )
        args = MagicMock(
            channel="C123456",
            event_number=1,
            minutes_before=10,
            message=["Test", "reminder", "message"],
            recurrence="daily",
        )
        blocks = get_setting_reminder_blocks(args, "test_slack_user_id")
        assert len(blocks) == 1
        assert "*10-minute reminder set for event " in blocks[0]["text"]["text"]
        mock_set_reminder.assert_called_once_with(
            channel="C123456",
            event_number=1,
            user_id="test_slack_user_id",
            minutes_before=10,
            recurrence="daily",
            message="Test reminder message",
        )
        mock_slack_scheduler.assert_called_once_with(mock_set_reminder.return_value)
        mock_slack_scheduler.return_value.schedule.assert_called_once()
        mock_slack_scheduler.send_message.assert_called_once()

    @patch("apps.nest.handlers.calendar_events.set_reminder")
    def test_get_setting_reminder_blocks_validation_error(self, mock_set_reminder):
        """Test get_setting_reminder_blocks function when ValidationError is raised."""
        mock_set_reminder.side_effect = ValidationError("Invalid event number.")
        args = MagicMock(
            channel="C123456",
            event_number=99,
            minutes_before=10,
            message=["Test", "reminder", "message"],
            recurrence="daily",
        )
        blocks = get_setting_reminder_blocks(args, "test_slack_user_id")
        assert len(blocks) == 1
        assert "*Invalid event number.*" in blocks[0]["text"]["text"]

    @patch("apps.nest.handlers.calendar_events.set_reminder")
    def test_get_setting_reminder_blocks_value_error(self, mock_set_reminder):
        """Test get_setting_reminder_blocks function when ValueError is raised."""
        mock_set_reminder.side_effect = ValueError("Some value error occurred.")
        args = MagicMock(
            channel="C123456",
            event_number=1,
            minutes_before=10,
            message=["Test", "reminder", "message"],
            recurrence="daily",
        )
        blocks = get_setting_reminder_blocks(args, "test_slack_user_id")
        assert len(blocks) == 1
        assert "*Some value error occurred.*" in blocks[0]["text"]["text"]

    @patch("apps.nest.handlers.calendar_events.set_reminder")
    def test_get_setting_reminder_blocks_service_error(self, mock_set_reminder):
        """Test get_setting_reminder_blocks function when service error occurs."""
        mock_set_reminder.side_effect = ServerNotFoundError()
        args = MagicMock(
            channel="C123456",
            event_number=1,
            minutes_before=10,
            message=["Test", "reminder", "message"],
            recurrence="daily",
        )
        blocks = get_setting_reminder_blocks(args, "test_slack_user_id")
        assert len(blocks) == 1
        assert "*Please check your internet connection.*" in blocks[0]["text"]["text"]
