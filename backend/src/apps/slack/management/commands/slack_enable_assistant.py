"""Enable the assistant for one Slack channel."""

from argparse import ArgumentParser

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
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
            conversation = Conversation.objects.filter(
                slack_channel_id=options["channel_id"]
            ).first()
            if conversation is not None and conversation.workspace_id != workspace.pk:
                message = "Channel already belongs to a different workspace."
                raise CommandError(message)
            if conversation is None or not conversation.has_slack_metadata:
                if not SlackConfig.app:
                    message = "Configure Slack before enabling an unsynchronized channel."
                    raise CommandError(message)
                try:
                    channel = SlackConfig.app.client.conversations_info(
                        channel=options["channel_id"]
                    )["channel"]
                except SlackApiError as error:
                    message = "Could not verify Slack channel privacy."
                    raise CommandError(message) from error
                if (
                    channel.get("id") != options["channel_id"]
                    or not isinstance(channel.get("is_private"), bool)
                    or channel.get("context_team_id") != options["workspace_id"]
                ):
                    message = "Slack returned incomplete or mismatched channel metadata."
                    raise CommandError(message)
                conversation = Conversation.update_data(channel, workspace)

            if conversation.workspace_id != workspace.pk:
                message = "Channel already belongs to a different workspace."
                raise CommandError(message)

            conversation.is_nest_bot_assistant_enabled = True
            conversation.save(update_fields=["is_nest_bot_assistant_enabled"])

        self.stdout.write(self.style.SUCCESS(f"Assistant enabled for {options['channel_id']}."))
