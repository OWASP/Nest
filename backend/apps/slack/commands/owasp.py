"""Slack bot owasp command."""

from apps.slack.apps import SlackConfig
from apps.slack.commands.command import CommandBase
from apps.slack.common.constants import COMMAND_HELP


class Owasp(CommandBase):
    """Slack bot /owasp command."""

    def all_commands(self):
        """Get all commands."""
        return [cls for cls in CommandBase.__subclasses__() if cls is not Owasp]

    def find_command(self, command_name):
        """Find the command class by name."""
        if not command_name:
            return None

        for cmd_class in self.all_commands():
            if cmd_class.__name__.lower() == command_name.lower():
                return cmd_class()
        return None

    def handler(self, ack, command, client):
        """Handle the command."""
        command_tokens = command["text"].split()
        cmd = self.find_command(command_tokens[0].strip().lower() if command_tokens else "")
        if cmd:
            command["text"] = " ".join(command_tokens[1:]).strip()
            return cmd.handler(ack, command, client)

        return super().handler(ack, command, client)

    def get_render_text(self, command):
        """Get the rendered text."""
        command_tokens = command["text"].split()
        if not command_tokens or command_tokens[0] in COMMAND_HELP:
            context = {
                "help": True,
                "command": self.get_command(),
            }
        else:
            cmd = command_tokens[0].strip().lower()
            context = {"help": False, "command": self.get_command(), "handler": cmd}

        return self.get_template_file().render(context)


if SlackConfig.app:
    Owasp().config_command()
