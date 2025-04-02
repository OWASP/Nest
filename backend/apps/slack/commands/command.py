"""Slack bot board command."""

from django.conf import settings

from apps.slack.apps import SlackConfig
from apps.slack.blocks import markdown
from apps.slack.template_system.loader import env
from apps.slack.utils import get_text


class CommandBase:
    def getRenderText(self, command, client):
        pass

    def getCommand(self):
        return f"/{self.__class__.__name__.lower()}"

    def getTemplateFile(self):
        return env.get_template(f"{self.__class__.__name__.lower()}.template")
    
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

        rendered_text = self.getRenderText(command, client)

        blocks = []
        for section in rendered_text.split("{{ SECTION_BREAK }}"):
                cleaned_section = section.strip()
                if cleaned_section:
                    blocks.append(markdown(cleaned_section))

        conversation = client.conversations_open(users=command["user_id"])
        client.chat_postMessage(
            blocks=blocks,
            channel=conversation["channel"]["id"],
            text=get_text(blocks),
        )

