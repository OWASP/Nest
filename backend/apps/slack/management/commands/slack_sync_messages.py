"""A command to populate Slack messages data for all conversations."""

import logging
import time

from django.core.management.base import BaseCommand
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.slack.models import Conversation, Message, Workspace

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Populate messages for all Slack conversations"

    def add_arguments(self, parser):
        """Define command line arguments."""
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of messages to retrieve per request",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.5,
            help="Delay between API requests in seconds",
        )
        parser.add_argument(
            "--channel-id",
            type=str,
            help="Specific channel ID to fetch messages from",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        channel_id = options["channel_id"]
        delay = options["delay"]
        include_threads = True

        workspaces = Workspace.objects.all()
        if not workspaces.exists():
            self.stdout.write(self.style.WARNING("No workspaces found in the database"))
            return

        for workspace in workspaces:
            self.stdout.write(f"\nProcessing workspace: {workspace.name}")

            if not (bot_token := workspace.bot_token):
                self.stdout.write(self.style.ERROR(f"No bot token found for {workspace}"))
                continue

            client = WebClient(token=bot_token)

            conversations = (
                Conversation.objects.filter(slack_channel_id=channel_id)
                if channel_id
                else Conversation.objects.filter(workspace=workspace)
            )

            for conversation in conversations:
                self._fetch_messages_for_conversation(
                    batch_size=batch_size,
                    client=client,
                    conversation=conversation,
                    delay=delay,
                    include_threads=include_threads,
                )

        self.stdout.write(self.style.SUCCESS("\nFinished processing all workspaces"))

    def _fetch_messages_for_conversation(
        self,
        client: WebClient,
        conversation: Conversation,
        batch_size: int,
        delay: float,
        *,
        include_threads: bool,
    ):
        """Fetch messages for a single conversation from its beginning."""
        self.stdout.write(f"\nProcessing channel: {conversation.name}")

        try:
            last_message = (
                Message.objects.filter(conversation=conversation).order_by("-timestamp").first()
            )
            oldest = (
                str(last_message.timestamp.timestamp())
                if last_message and last_message.timestamp
                else None
            )

            cursor = None
            has_more = True

            while has_more:
                response = client.conversations_history(
                    channel=conversation.slack_channel_id,
                    cursor=cursor,
                    limit=batch_size,
                    oldest=oldest,
                )
                self._handle_slack_response(response, "conversations_history")
                messages_data = response.get("messages", [])

                messages = [
                    message
                    for message_data in messages_data
                    if (
                        message := self._create_message_from_data(
                            client, message_data, conversation, include_threads=include_threads
                        )
                    )
                ]

                messages_count = len(messages)
                if messages:
                    Message.bulk_save(messages)
                    self.stdout.write(f"Saved {messages_count} messages")

                cursor = response.get("response_metadata", {}).get("next_cursor")
                has_more = bool(cursor)

                if delay and has_more:
                    time.sleep(delay)

            self.stdout.write(
                self.style.SUCCESS(f"Finished processing messages from {conversation.name}")
            )

        except SlackApiError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch messages for {conversation.name}: {e.response['error']}"
                )
            )

    def _create_message_from_data(
        self,
        client: WebClient,
        message_data: dict,
        conversation: Conversation,
        *,
        include_threads: bool,
    ) -> Message | None:
        """Create Message instance from Slack API data."""
        try:
            if message_data.get("subtype") in ["channel_join", "channel_leave"]:
                return None

            if (
                not message_data.get("text")
                and not message_data.get("attachments")
                and not message_data.get("files")
            ):
                return None

            message_ts = message_data.get("ts")
            thread_ts = message_data.get("thread_ts")

            is_actual_thread_parent = message_data.get("reply_count", 0) > 0
            is_reply_in_thread = thread_ts is not None and thread_ts != message_ts

            if include_threads and is_reply_in_thread:
                return None

            message_dict = {
                "slack_message_id": message_ts,
                "conversation": conversation,
                "text": message_data.get("text", ""),
                "timestamp": message_ts,
                "is_thread": is_actual_thread_parent,
            }

            if include_threads and is_actual_thread_parent:
                try:
                    thread_response = client.conversations_replies(
                        channel=conversation.slack_channel_id,
                        ts=message_ts,
                    )
                    self._handle_slack_response(thread_response, "conversations_replies")

                    if thread_response.get("ok"):
                        api_thread_messages = thread_response.get("messages", [])
                        current_parent_text = message_dict.get("text", "")
                        combined_text_list = [current_parent_text]

                        reply_texts = [
                            reply_msg_data.get("text", "")
                            for reply_msg_data in api_thread_messages[1:]
                            if reply_msg_data.get("text", "")
                        ]
                        combined_text_list.extend(reply_texts)

                        message_dict["text"] = "\n\n".join(filter(None, combined_text_list))

                except SlackApiError:
                    logger.warning("Failed to fetch thread replies")

            return Message.update_data(message_dict, save=False)

        except KeyError:
            logger.warning("Invalid message data")
            return None

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
