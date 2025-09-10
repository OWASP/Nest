"""Test cases for Nest calendar events utilities."""

from apps.nest.utils.calendar_events import parse_reminder_args


class TestCalendarEventsUtils:
    """Test cases for Nest calendar events utilities."""

    def test_parse_reminder_args_all_args(self):
        """Test parse_reminder_args with all arguments provided."""
        text = (
            "--channel C123456 --event_number 1 --minutes_before 15 "
            '--message "Meeting with team" --recurrence weekly'
        )
        args = parse_reminder_args(text)
        assert args.channel == "C123456"
        assert args.event_number == 1
        assert args.minutes_before == 15
        assert args.message == ["Meeting with team"]
        assert args.recurrence == "weekly"

    def test_parse_reminder_args_missing_optional_args(self):
        """Test parse_reminder_args with only required arguments."""
        text = "--channel C123456 --event_number 2"
        args = parse_reminder_args(text)
        assert args.channel == "C123456"
        assert args.event_number == 2
        assert args.minutes_before == 10  # Default value
        assert args.message == []  # Default value
        assert args.recurrence == "once"  # Default value
