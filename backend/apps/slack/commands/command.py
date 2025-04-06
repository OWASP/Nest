"""Slack bot board command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text
from apps.slack.commands import *


class CommandBase:
    """Base class for Slack commands."""
    
    @staticmethod
    def get_all_commands():
        """Get all commands."""
        return [cls for cls in CommandBase.__subclasses__()] 
    
    @staticmethod
    def config_all_commands():
        for cmd_class in CommandBase.get_all_commands():
            cmd_class().config_command()
    
    def get_render_text(self, command):
        """Get the rendered text.

        Args:
            command (dict): The Slack command payload.

        Returns:
            str: The rendered text.

        """
        template = self.get_template_file()
        return template.render()

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
        return env.get_template(self.get_template_file_name())

    def get_template_file_name(self):
        """Get the template file name."""
        return f"{self.__class__.__name__.lower()}.template"

    def config_command(self):
        """Command configuration."""
        SlackConfig.app.command(self.get_command())(self.handler)
    
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

        blocks = self.get_render_blocks(command)
        conversation = client.conversations_open(users=command["user_id"])
        client.chat_postMessage(
            blocks=blocks,
            channel=conversation["channel"]["id"],
            text=get_text(blocks),
        )