"""Slack bot owasp command."""

from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_HELP


class Owasp(CommandBase):
    """Slack bot /owasp command."""

    def find_command(self, command_name: str):
        """Find the command class by name."""
        if not command_name:
            return None

        for cmd_class in (
            cls for cls in CommandBase.get_commands() if cls is not Owasp
        ):
            if cmd_class.__name__.lower() == command_name.lower():
                return cmd_class()
        return None

    def handler(self, ack, command, client):
        """Handle the command."""
        command_tokens = command["text"].split()
        first_token = command_tokens[0].strip().lower() if command_tokens else ""

        # Handle /owasp ask <query> subcommand
        if first_token == "ask":
            command["text"] = " ".join(command_tokens[1:]).strip()
            return self._handle_ask(ack, command, client)

        cmd = self.find_command(first_token)
        if cmd:
            command["text"] = " ".join(command_tokens[1:]).strip()
            return cmd.handler(ack, command, client)

        return super().handler(ack, command, client)

    def _handle_ask(self, ack, command, client):
        """Handle the /owasp ask <query> subcommand.

        Args:
            ack: Slack acknowledgement callable.
            command (dict): The Slack command payload.
            client: The Slack WebClient instance.

        """
        from apps.slack.common.handlers.ai import get_blocks

        ack()
        query = command.get("text", "").strip()
        if not query:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please provide a question. Usage: `/owasp ask <your question>`",
                    },
                }
            ]
        else:
            blocks = get_blocks(query=query)

        channel_id = client.conversations_open(users=command["user_id"])["channel"][
            "id"
        ]
        client.chat_postMessage(
            channel=channel_id,
            blocks=blocks,
            text=query or "Please provide a question.",
        )

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        command_tokens = command["text"].split()
        if not command_tokens or command_tokens[0] in COMMAND_HELP:
            return {**super().get_context(command), "HELP": True}
        return {
            **super().get_context(command),
            "HANDLER": command_tokens[0].strip().lower(),
            "HELP": False,
        }
