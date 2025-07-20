"""Base class and common functionality for Slack commands."""

import logging
from pathlib import Path

from django.conf import settings
from jinja2 import Template

from apps.common.constants import NL
from apps.common.utils import convert_to_snake_case
from apps.slack.apps import SlackConfig
from apps.slack.blocks import DIVIDER, SECTION_BREAK, markdown
from apps.slack.constants import FEEDBACK_SHARING_INVITE, NEST_BOT_NAME
from apps.slack.template_loader import env
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


class CommandBase:
    """Base class for Slack commands."""

    @staticmethod
    def configure_commands():
        """Configure commands."""
        if SlackConfig.app is None:
            logger.warning("SlackConfig.app is None. Command handlers are not registered.")
            return

        for command in CommandBase.get_commands():
            command().register()

    @staticmethod
    def get_commands():
        """Get all commands."""
        yield from CommandBase.__subclasses__()

    @property
    def command_name(self) -> str:
        """Get the command name."""
        return f"/{self.__class__.__name__.lower()}"

    @property
    def template(self) -> Template:
        """Get the template file.

        Returns:
            Template: The Jinja2 template object.

        """
        return env.get_template(str(self.template_path))

    @property
    def template_path(self) -> Path:
        """Get the template file name."""
        return Path(f"commands/{convert_to_snake_case(self.__class__.__name__)}.jinja")

    def get_context(self, command) -> dict:
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            "COMMAND": self.command_name,
            "DIVIDER": DIVIDER,
            "FEEDBACK_SHARING_INVITE": FEEDBACK_SHARING_INVITE,
            "NEST_BOT_NAME": NEST_BOT_NAME,
            "NL": NL,
            "SECTION_BREAK": SECTION_BREAK,
            "USER_ID": self.get_user_id(command),
        }

    def get_user_id(self, command) -> str:
        """Get the user ID from the command.

        Args:
            command (dict): The Slack event payload.

        Returns:
            str: The user ID.

        """
        return command.get("user_id")

    def render_blocks(self, command):
        """Get the rendered blocks.

        Args:
            command (dict): The Slack command payload.

        Returns:
            list: The rendered blocks.

        """
        blocks = []
        for section in self.render_text(self.get_context(command)).split(SECTION_BREAK):
            if section.strip() == DIVIDER:
                blocks.append({"type": "divider"})
            elif section:
                blocks.append(markdown(section))

        return blocks

    def render_text(self, context) -> str:
        """Get the rendered text.

        Args:
            context: The Slack command payload.

        Returns:
            str: The rendered text.

        """
        return self.template.render(context)

    def handler(self, ack, command, client):
        """Handle the Slack command.

        Args:
            ack (function): Acknowledge the Slack command request.
            command (dict): The Slack command payload.
            client (slack_sdk.WebClient): The Slack WebClient instance for API calls.

        """
        ack()

        if not settings.SLACK_COMMANDS_ENABLED:
            return

        try:
            if blocks := self.render_blocks(command):
                client.chat_postMessage(
                    blocks=blocks,
                    channel=client.conversations_open(
                        users=self.get_user_id(command),
                    )["channel"]["id"],
                    text=get_text(blocks),
                )
        except Exception:
            logger.exception("Failed to handle command '%s'", self.command_name)
            blocks = [markdown(":warning: An error occurred. Please try again later.")]
            client.chat_postMessage(
                blocks=blocks,
                channel=client.conversations_open(
                    users=self.get_user_id(command),
                )["channel"]["id"],
                text=get_text(blocks),
            )

    def register(self):
        """Register this command handler with the Slack app."""
        SlackConfig.app.command(self.command_name)(self.handler)
