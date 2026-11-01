"""Enable the assistant for one Slack channel."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.slack.models import Conversation, Workspace


class Command(BaseCommand):
    help = "Create local Slack records if needed and enable the assistant for one channel."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Require the Slack workspace and channel identifiers."""
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--channel-id", required=True)

    def handle(self, *_args, **options) -> None:
        """Enable the channel without changing its workspace or other settings."""
        with transaction.atomic():
            workspace, _ = Workspace.objects.get_or_create(
                slack_workspace_id=options["workspace_id"],
            )
            conversation, _ = Conversation.objects.get_or_create(
                slack_channel_id=options["channel_id"],
                defaults={"workspace": workspace, "is_channel": True},
            )
            if conversation.workspace_id != workspace.pk:
                message = "Channel already belongs to a different workspace."
                raise CommandError(message)

            conversation.is_nest_bot_assistant_enabled = True
            conversation.save(update_fields=["is_nest_bot_assistant_enabled"])

        self.stdout.write(self.style.SUCCESS(f"Assistant enabled for {options['channel_id']}."))
