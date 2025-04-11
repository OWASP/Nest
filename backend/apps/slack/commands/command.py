"""Base class and common functionality for Slack commands."""

import logging

from django.conf import settings

from apps.common.constants import NL
from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text

logger = logging.getLogger(__name__)


class CommandBase:
    """Base class for Slack commands.

    Template formatting notes:
    - Use "{{ SECTION_BREAK }}" to separate content into different Slack blocks
    - Use "{{ DIVIDER }}" to insert a horizontal divider
    """

    @staticmethod
    def get_all_commands():
        """Get all commands."""
        return list(CommandBase.__subclasses__())

    @staticmethod
    def config_all_commands():
        """Configure all commands."""
        for cmd_class in CommandBase.get_all_commands():
            cmd_class().config_command()

    def get_render_text(self, command):
        """Get the rendered text.

        Args:
            command: The Slack command payload.

        Returns:
            str: The rendered text.

        """
        template = self.get_template_file()
        return template.render(**self.get_template_context(command))

    def get_template_context(self, command):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        return {
            "command": self.get_command(),
            "NL": NL,
            "SECTION_BREAK": "{{ SECTION_BREAK }}",
            "DIVIDER": "{{ DIVIDER }}",
        }

    def get_render_blocks(self, command):
        """Get the rendered blocks.

        Args:
            command (dict): The Slack command payload.

        Returns:
            list: The rendered blocks.

        """
        rendered_text = self.get_render_text(command)
        blocks = []
        for section in rendered_text.split("{{ SECTION_BREAK }}"):
            if section == "{{ DIVIDER }}":
                blocks.append({"type": "divider"})
            elif section:
                blocks.append(markdown(section))
        return blocks

    def get_command(self):
        """Get the command name."""
        return f"/{self.__class__.__name__.lower()}"

    def get_template_file(self):
        """Get the template file.

        Returns:
            Template: The Jinja2 template object.

        """
        template_name = self.get_template_file_name()
        try:
            return env.get_template(template_name)
        except Exception:
            logger.exception(
                "Failed to load template '%s' for command '%s'", template_name, self.get_command()
            )
            raise

    def get_template_file_name(self):
        """Get the template file name."""
        return f"{self.__class__.__name__.lower()}.template"

    def config_command(self):
        """Command configuration."""
        if SlackConfig.app is not None:
            SlackConfig.app.command(self.get_command())(self.handler)
        else:
            logger.warning(
                "SlackConfig.app is None. Command '%s' not registered.", self.get_command()
            )

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
            blocks = self.get_render_blocks(command)
            conversation = client.conversations_open(users=command["user_id"])
            client.chat_postMessage(
                blocks=blocks,
                channel=conversation["channel"]["id"],
                text=get_text(blocks),
            )
        except Exception:
            logger.exception("Failed to handle command '%s'", self.get_command())
            conversation = client.conversations_open(users=command["user_id"])
            client.chat_postMessage(
                blocks=[markdown(":warning: An error occurred. Please try again later.")],
                channel=conversation["channel"]["id"],
                text="An error occurred while processing your command.",
            )
