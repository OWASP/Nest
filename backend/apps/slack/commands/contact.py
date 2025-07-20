"""Slack bot contact command."""

from apps.slack.commands.command import CommandBase


class Contact(CommandBase):
    """Slack bot /contact command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_context(command),
            "CONTACT_PAGE_NAME": "OWASP contact",
            "CONTACT_PAGE_URL": "https://owasp.org/contact/",
        }
