"""A command to populate Slack channels and members data based on workspaces's bot tokens."""

import logging
import time

from django.core.management.base import BaseCommand
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.slack.models import Conversation, Member, Workspace

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate channels and members for all Slack workspaces using their bot tokens"

    def add_arguments(self, parser):
        """Define command line arguments."""
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of conversations to retrieve per request",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.5,
            help="Delay between API requests in seconds",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        delay = options["delay"]

        workspaces = Workspace.objects.all()
        if not workspaces.exists():
            self.stdout.write(self.style.WARNING("No workspaces found in the database"))
            return

        for workspace in workspaces:
            self.stdout.write(f"\nProcessing workspace: {workspace}")

            if not (bot_token := workspace.bot_token):
                self.stdout.write(self.style.ERROR(f"No bot token found for {workspace}"))
                continue

            client = WebClient(token=bot_token)

            self.stdout.write(f"Fetching conversations for {workspace}...")
            conversations = []
            total_channels = 0
            try:
                cursor = None
                while True:
                    response = client.conversations_list(
                        cursor=cursor,
                        exclude_archived=False,
                        limit=batch_size,
                        timeout=30,
                        types="public_channel,private_channel",
                    )
                    self._handle_slack_response(response, "conversations_list")

                    conversations.extend(
                        member
                        for conversation_data in response["channels"]
                        if (member := Conversation.update_data(conversation_data, workspace))
                    )
                    total_channels += len(response["channels"])

                    if not (cursor := response.get("response_metadata", {}).get("next_cursor")):
                        break

                    if delay:
                        time.sleep(delay)
            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch conversations: {e.response['error']}")
                )
            if conversations:
                Conversation.bulk_save(conversations)
                self.stdout.write(self.style.SUCCESS(f"Populated {total_channels} channels"))

            self.stdout.write(f"Fetching members for {workspace}...")
            members = []
            total_members = 0
            try:
                cursor = None
                while True:
                    response = client.users_list(
                        cursor=cursor,
                        limit=batch_size,
                        timeout=30,
                    )
                    self._handle_slack_response(response, "users_list")

                    members.extend(
                        member
                        for member_data in response["members"]
                        if (member := Member.update_data(member_data, workspace))
                    )
                    total_members += len(response["members"])

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    if not cursor:
                        break
            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch members: {e.response['error']}")
                )
            if members:
                Member.bulk_save(members)
                self.stdout.write(self.style.SUCCESS(f"Populated {total_members} members"))

        self.stdout.write(self.style.SUCCESS("\nFinished processing all workspaces"))

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
