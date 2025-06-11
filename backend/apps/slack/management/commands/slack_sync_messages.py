"""A command to populate Slack messages data for all conversations."""

import logging
import time

from django.core.management.base import BaseCommand
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.slack.models import Conversation, Member, Message, Workspace

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
            parent_messages = self._fetch_parent_messages(
                client=client, conversation=conversation, batch_size=batch_size, delay=delay
            )

            if include_threads:
                self._fetch_thread_replies(
                    client=client,
                    conversation=conversation,
                    parent_messages=parent_messages,
                    delay=delay,
                )

            self.stdout.write(
                self.style.SUCCESS(f"Finished processing messages from {conversation.name}")
            )

        except SlackApiError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch messages for {conversation.name}: {e.response['error']}"
                )
            )

    def _fetch_parent_messages(
        self, client: WebClient, conversation: Conversation, batch_size: int, delay: float
    ) -> list[Message]:
        """Fetch all parent messages (non-thread) for a conversation."""
        cursor = None
        has_more = True
        batch_messages = []
        all_threaded_parents = []

        last_message = (
            Message.objects.filter(conversation=conversation).order_by("-created_at").first()
        )
        oldest = last_message.created_at.timestamp() if last_message else None

        while has_more:
            try:
                response = client.conversations_history(
                    channel=conversation.slack_channel_id,
                    cursor=cursor,
                    limit=batch_size,
                    oldest=oldest,
                )
                self._handle_slack_response(response, "conversations_history")

                for message_data in response.get("messages", []):
                    if message_data.get("thread_ts") and message_data.get(
                        "ts"
                    ) != message_data.get("thread_ts"):
                        continue

                    message = self._create_message_from_data(
                        client=client,
                        message_data=message_data,
                        conversation=conversation,
                        is_thread_reply=False,
                        parent_message=None,
                    )

                    if message:
                        batch_messages.append(message)
                        if message.is_thread_parent:
                            all_threaded_parents.append(message)

                if batch_messages:
                    Message.bulk_save(batch_messages)
                    batch_messages = []

                cursor = response.get("response_metadata", {}).get("next_cursor")
                has_more = bool(cursor)

                if delay and has_more:
                    time.sleep(delay)

            except SlackApiError as e:
                self.stdout.write(
                    self.style.ERROR(f"Error fetching messages: {e.response['error']}")
                )
                break

        return all_threaded_parents

    def _fetch_thread_replies(
        self,
        client: WebClient,
        conversation: Conversation,
        parent_messages: list[Message],
        delay: float,
    ):
        """Fetch all thread replies for parent messages."""
        if not parent_messages:
            return

        replies_to_save = []

        for parent_message in parent_messages:
            try:
                latest_reply = (
                    Message.objects.filter(
                        conversation=conversation,
                        parent_message=parent_message,
                    )
                    .order_by("-created_at")
                    .first()
                )
                oldest_ts = latest_reply.created_at.timestamp() if latest_reply else None

                cursor = None
                has_more = True
                thread_reply_count = 0

                while has_more:
                    params = {
                        "channel": conversation.slack_channel_id,
                        "ts": parent_message.slack_message_id,
                        "cursor": cursor,
                        "limit": 100,
                        "inclusive": True,
                    }
                    if oldest_ts:
                        params["oldest"] = str(oldest_ts)

                    response = client.conversations_replies(**params)
                    self._handle_slack_response(response, "conversations_replies")

                    messages_in_response = response.get("messages", [])
                    if not messages_in_response:
                        break

                    for reply_data in messages_in_response[1:]:
                        reply = self._create_message_from_data(
                            client=client,
                            message_data=reply_data,
                            conversation=conversation,
                            is_thread_reply=True,
                            parent_message=parent_message,
                        )
                        if reply:
                            replies_to_save.append(reply)
                            thread_reply_count += 1

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    has_more = bool(cursor)

                    if delay and has_more:
                        time.sleep(delay)

            except SlackApiError:
                self.stdout.write(self.style.ERROR("Failed to fetch thread replies for message"))

        if replies_to_save:
            batch_size = 1000
            for i in range(0, len(replies_to_save), batch_size):
                batch = replies_to_save[i : i + batch_size]
                Message.bulk_save(batch)

    def _create_message_from_data(
        self,
        client: WebClient,
        message_data: dict,
        conversation: Conversation,
        *,
        is_thread_reply: bool = False,
        parent_message: Message | None = None,
    ) -> Message | None:
        """Create Message instance using from_slack pattern."""
        try:
            if message_data.get("subtype") in {"channel_join", "channel_leave", "bot_message"}:
                return None
            if not any(
                [
                    message_data.get("text"),
                    message_data.get("attachments"),
                    message_data.get("files"),
                    message_data.get("blocks"),
                ]
            ):
                return None

            slack_user_id = message_data.get("user") or message_data.get("bot_id")
            if not slack_user_id:
                return None

            try:
                author = Member.objects.get(
                    slack_user_id=slack_user_id, workspace=conversation.workspace
                )
            except Member.DoesNotExist:
                try:
                    user_info = client.users_info(user=slack_user_id)
                    self._handle_slack_response(user_info, "users_info")

                    user_data = user_info["user"]
                    author = Member.update_data(user_data, conversation.workspace, save=True)

                    self.stdout.write(self.style.SUCCESS(f"Created new member: {slack_user_id}"))
                except SlackApiError as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Failed to fetch user data for {slack_user_id}: {e.response['error']}"
                        )
                    )
                    return None

            return Message.update_data(
                data=message_data,
                conversation=conversation,
                author=author,
                is_thread_reply=is_thread_reply,
                parent_message=parent_message,
                save=False,
            )

        except Exception:
            logger.exception("Error creating message from data")
            return None

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
