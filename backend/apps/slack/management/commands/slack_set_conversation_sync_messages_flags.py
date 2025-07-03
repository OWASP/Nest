"""A command to set Slack conversations sync messages flags."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from apps.slack.models import Conversation, Workspace

SYNC_MESSAGES_CONVERSATIONS = {
    "askowasp",
    "chapter-committee",
    "chapters",
    "contribute",
    "events-committee",
    "gsoc",
    "leaders",
    "owasp-community",
    "project-committee",
    "project-nest",
    "projects",
    "sponsorship",
    "virtual-events",
}


class Command(BaseCommand):
    help = "Set sync messages flag for Slack conversations."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """

    def handle(self, *_args, **options) -> None:
        """Handle the command execution."""
        # Disable syncing for all.
        Conversation.objects.update(sync_messages=False)

        # Enable syncing for whitelisted conversations.
        Conversation.objects.filter(
            is_private=False,
            name__in=SYNC_MESSAGES_CONVERSATIONS,
            workspace=Workspace.get_default_workspace(),
        ).update(sync_messages=True)
