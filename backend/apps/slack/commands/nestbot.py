"""Slack NestBot root command."""

from apps.slack.blocks import markdown
from apps.slack.commands.command import CommandBase


class NestBot(CommandBase):
    """Slack NestBot Command."""

    @property
    def command_name(self):
        """Return the command name."""
        return "/nestbot"

    def render_blocks(self, command):
        """Render the blocks for the command."""
        from apps.nest.utils.calendar_events import parse_cancel_reminder_args, parse_reminder_args
        from apps.slack.common.handlers.calendar_events import (
            get_cancel_reminder_blocks,
            get_setting_reminder_blocks,
        )

        try:
            args = parse_cancel_reminder_args(command.get("text", ""))
        except SystemExit:  # NOSONAR
            try:
                args = parse_reminder_args(command.get("text", ""))
            except SystemExit:  # NOSONAR
                return [
                    markdown("*Invalid command format. Please check your input and try again.*")
                ]
            else:
                return get_setting_reminder_blocks(
                    args, self.get_user_id(command), self.get_workspace_id(command)
                )
        else:
            return get_cancel_reminder_blocks(int(args.number), self.get_user_id(command))
