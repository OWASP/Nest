"""Slack bot news command."""

from apps.common.constants import OWASP_NEWS_URL
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_news_data


class News(CommandBase):
    """Slack bot /news command."""

    def get_template_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            **super().get_template_context(command),
            "news_items": get_news_data(),
            "news_url": OWASP_NEWS_URL,
        }
