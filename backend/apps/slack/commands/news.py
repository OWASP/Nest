"""Slack bot news command."""

from apps.common.constants import NL, OWASP_NEWS_URL
from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.utils import get_news_data


class News(CommandBase):
    """Slack bot /news command."""

    def get_render_text(self, command):
        """Get the rendered text."""
        items = get_news_data()
        if items:
            return self.get_template_file().render(
                has_news=True,
                news_items=items,
                news_url=OWASP_NEWS_URL,
                SECTION_BREAK="{{ SECTION_BREAK }}",
                DIVIDER="{{ DIVIDER }}",
                NL=NL,
            )
        return self.get_template_file().render(
            has_news=False,
            NL=NL,
        )


if SlackConfig.app:
    News().config_command()
