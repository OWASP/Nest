"""Slack command to cancel a reminder."""

from apps.slack.blocks import markdown
from apps.slack.commands.command import CommandBase


class CancelReminder(CommandBase):
    """Slack Cancel Reminder Command Class."""

    @property
    def command_name(self) -> str:
        """Get the command name."""
        return "/cancel-reminder"

    def render_blocks(self, command):
        """Render the blocks for the command."""
        from apps.nest.utils.calendar_events import parse_cancel_reminder_args
        from apps.slack.common.handlers.calendar_events import get_cancel_reminder_blocks

        try:
            args = parse_cancel_reminder_args(command.get("text", ""))
        except SystemExit:  # NOSONAR
            return [
                markdown("*Invalid command arguments. Please check your input and try again.*")
            ]
        else:
            return get_cancel_reminder_blocks(int(args.number), self.get_user_id(command))
