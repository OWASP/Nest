"""Slack Set Reminder Command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.calendar_events import get_reminder_blocks
from apps.slack.utils import parse_slack_reminder_args


class SetReminder(CommandBase):
    """Slack Set Reminder Command."""

    @property
    def command_name(self):
        """Return the command name."""
        return "/set-reminder"

    def render_blocks(self, command):
        """Render the blocks for the command."""
        args = parse_slack_reminder_args(command["text"])
        return get_reminder_blocks(args, self.get_user_id(command))
