"""Management command to sync Slack workspaces, channels, and members."""

import logging
import time
import os
import random
import secrets
import time

from django.core.management.base import BaseCommand
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.slack.models import Conversation, Member, Workspace

logger = logging.getLogger(__name__)
MAX_RETRIES = 5


class Command(BaseCommand):
    help = "Populate channels and members for all Slack workspaces using their bot tokens"

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=1000)
        parser.add_argument("--delay", type=float, default=0.5)

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        delay = options["delay"]

        workspaces = Workspace.objects.all()
        if not workspaces.exists():
            self.stdout.write(self.style.WARNING("No workspaces found in the database"))
            return

        for workspace in workspaces:
            self.stdout.write(f"\nProcessing workspace: {workspace}")
            bot_token = (
                (getattr(workspace, "bot_token", "") or "").strip()
                or os.environ.get("DJANGO_SLACK_BOT_TOKEN")
            )
            if not bot_token:
                self.stdout.write(self.style.ERROR(f"No bot token found for {workspace}"))
                continue

            client = WebClient(token=bot_token)

            self._fetch_conversations(client, workspace, batch_size, delay)
            self._fetch_members(client, workspace, batch_size, delay)

        self.stdout.write(self.style.SUCCESS("\nFinished processing all workspaces"))

    def _call_slack_api(self, func, *args, **kwargs):
        def _raise_max_retries():
            raise RuntimeError("Max retries exceeded while calling Slack API")
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = func(*args, **kwargs)
                if not response.get("ok", False):
                    raise RuntimeError(f"{func.__name__} returned ok=False: {response!r}")
                return response
            except SlackApiError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    self.stdout.write(
                        self.style.WARNING(f"Rate limited. Sleeping {retry_after}s...")
                    )
                    time.sleep(retry_after)
                else:
                    raise
            retries += 1
            backoff = 2**retries + secrets.randbelow(1000) / 1000
            time.sleep(backoff)
        _raise_max_retries()
        return  # explicit return to satisfy RET503

    def _fetch_conversations(self, client, workspace, batch_size, delay):
        self.stdout.write(f"Fetching conversations for {workspace}...")
        conversations = []
        total_channels = 0
        try:
            cursor = None
            while True:
                response = self._call_slack_api(
                    client.conversations_list,
                    cursor=cursor,
                    exclude_archived=False,
                    limit=batch_size,
                    timeout=30,
                    types="public_channel,private_channel",
                )

                for conversation_data in response["channels"]:
                    if "num_members" not in conversation_data:
                        try:
                            info = self._call_slack_api(
                                client.conversations_info,
                                channel=conversation_data["id"],
                                include_num_members=True,
                            )
                            conversation_data["num_members"] = info["channel"].get("num_members")
                        except SlackApiError as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Failed to get member count for {conversation_data['id']}: {e}"
                                )
                            )
                            conversation_data["num_members"] = None

                    if (conversation := Conversation.update_data(conversation_data, workspace)):
                        conversations.append(conversation)

                total_channels += len(response["channels"])
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                time.sleep(delay)
        except SlackApiError as e:
            self.stdout.write(self.style.ERROR(f"Error fetching conversations: {e}"))

        if conversations:
            Conversation.bulk_save(conversations)
            self.stdout.write(self.style.SUCCESS(f"Populated {total_channels} channels"))

    def _fetch_members(self, client, workspace, batch_size, delay):
        self.stdout.write(f"Fetching members for {workspace}...")
        members = []
        total_members = 0
        try:
            cursor = None
            while True:
                response = self._call_slack_api(
                    client.users_list,
                    cursor=cursor,
                    limit=batch_size,
                    timeout=30,
                )

                members.extend(
                    member
                    for member_data in response["members"]
                    if (member := Member.update_data(member_data, workspace))
                )
                total_members += len(response["members"])
                cursor = response.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
                time.sleep(delay)
        except SlackApiError as e:
            self.stdout.write(self.style.ERROR(f"Error fetching members: {e}"))

        if members:
            Member.bulk_save(members)
            self.stdout.write(self.style.SUCCESS(f"Populated {total_members} members"))
