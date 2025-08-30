"""Slack Google sign-in command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.handlers.google_sign_in import get_blocks


class GoogleSignIn(CommandBase):
    """Slack Google sign-in command."""

    @property
    def command_name(self):
        """Return the command name."""
        # TODO(arkid15r): change command to something more related to OWASP Nest
        # (e.g. /nest or /nestbot).
        return "/google-sign-in"

    def render_blocks(self, command):
        """Render the blocks for the command."""
        return get_blocks(self.get_user_id(command))
