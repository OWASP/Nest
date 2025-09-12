"""Slack Set Reminder Command."""

from apps.nest.utils.calendar_events import parse_reminder_args
from apps.slack.blocks import markdown
from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.calendar_events import get_reminder_blocks


class SetReminder(CommandBase):
    """Slack Set Reminder Command."""

    @property
    def command_name(self):
        """Return the command name."""
        return "/set-reminder"

    def render_blocks(self, command):
        """Render the blocks for the command."""
        try:
            args = parse_reminder_args(command["text"])
        except SystemExit:
            return [markdown("*Invalid command format. Please check your input and try again.*")]
        else:
            return get_reminder_blocks(args, self.get_user_id(command))
