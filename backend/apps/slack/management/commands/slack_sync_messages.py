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
            default=4,
            help="Delay between API requests in seconds",
        )
        parser.add_argument(
            "--channel-id",
            type=str,
            help="Specific channel ID to fetch messages from",
        )
        parser.add_argument(
            "--max-retries",
            type=int,
            default=5,
            help="Maximum retries for rate-limited requests",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        channel_id = options["channel_id"]
        delay = options["delay"]
        max_retries = options["max_retries"]

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
                self._fetch_conversation(
                    batch_size=batch_size,
                    client=client,
                    conversation=conversation,
                    delay=delay,
                    max_retries=max_retries,
                    include_replies=True,
                )

        self.stdout.write(self.style.SUCCESS("\nFinished processing all workspaces"))

    def _fetch_conversation(
        self,
        client: WebClient,
        conversation: Conversation,
        batch_size: int,
        delay: float,
        max_retries: int,
        *,
        include_replies: bool = True,
    ):
        """Fetch messages for a single conversation from its beginning."""
        self.stdout.write(f"\nProcessing channel: {conversation.name}")

        try:
            messages = self._fetch_messages(
                client=client,
                conversation=conversation,
                batch_size=batch_size,
                delay=delay,
                max_retries=max_retries,
            )

            if include_replies:
                for message in messages:
                    self._fetch_replies(
                        client=client,
                        conversation=conversation,
                        message=message,
                        delay=delay,
                        max_retries=max_retries,
                    )
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

    def _fetch_messages(
        self,
        client: WebClient,
        conversation: Conversation,
        batch_size: int,
        delay: float,
        max_retries: int,
    ) -> list[Message]:
        """Fetch all parent messages (non-thread) for a conversation."""
        cursor = None
        has_more = True
        batch_messages = []
        all_threaded_parents = []
        retry_count = 0

        latest_message = (
            Message.objects.filter(conversation=conversation).order_by("-created_at").first()
        )

        while has_more:
            try:
                response = client.conversations_history(
                    channel=conversation.slack_channel_id,
                    cursor=cursor,
                    limit=batch_size,
                    oldest=latest_message.created_at.timestamp() if latest_message else None,
                )
                self._handle_slack_response(response, "conversations_history")

                for message_data in response.get("messages", []):
                    if message_data.get("thread_ts") and message_data.get(
                        "ts"
                    ) != message_data.get("thread_ts"):
                        continue

                    message = self._create_message_from_data(
                        client=client,
                        conversation=conversation,
                        delay=delay,
                        max_retries=max_retries,
                        message_data=message_data,
                    )

                    if message:
                        batch_messages.append(message)
                        if message.has_replies:
                            all_threaded_parents.append(message)

                if batch_messages:
                    Message.bulk_save(batch_messages)
                    batch_messages = []

                cursor = response.get("response_metadata", {}).get("next_cursor")
                has_more = bool(cursor)

                if delay and has_more:
                    time.sleep(delay)

                retry_count = 0

            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    if retry_count >= max_retries:
                        self.stdout.write(
                            self.style.ERROR(f"Max retries ({max_retries}) exceeded for history")
                        )
                        break

                    retry_after = int(
                        e.response.headers.get("Retry-After", delay * (retry_count + 1))
                    )
                    retry_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Rate limited. Retrying after {retry_after} seconds")
                    )
                    time.sleep(retry_after)
                    continue
                self.stdout.write(
                    self.style.ERROR(f"Error fetching messages: {e.response['error']}")
                )
                break

        return all_threaded_parents

    def _fetch_replies(
        self,
        client: WebClient,
        conversation: Conversation,
        message: Message,
        delay: float,
        max_retries: int,
    ):
        """Fetch all thread replies for parent messages."""
        if not message:
            return

        replies_to_save = []

        try:
            latest_reply = (
                Message.objects.filter(
                    conversation=conversation,
                    parent_message=message,
                )
                .order_by("-created_at")
                .first()
            )
            oldest_ts = latest_reply.created_at.timestamp() if latest_reply else None

            cursor = None
            has_more = True
            retry_count = 0

            while has_more:
                try:
                    params = {
                        "channel": conversation.slack_channel_id,
                        "ts": message.slack_message_id,
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
                            delay=delay,
                            max_retries=max_retries,
                            parent_message=message,
                        )
                        if reply:
                            replies_to_save.append(reply)

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    has_more = bool(cursor)

                    if delay and has_more:
                        time.sleep(delay)

                    retry_count = 0

                except SlackApiError as e:
                    if e.response["error"] == "ratelimited":
                        if retry_count >= max_retries:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Max retries ({max_retries}) exceeded for thread"
                                )
                            )
                            break

                        retry_after = int(
                            e.response.headers.get("Retry-After", delay * (retry_count + 1))
                        )
                        retry_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Rate limited. Retrying after {retry_after} seconds"
                            )
                        )
                        time.sleep(retry_after)
                        continue
                    raise

        except SlackApiError as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch thread replies for message: {e.response['error']}"
                )
            )

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
        delay: float,
        max_retries: int,
        *,
        parent_message: Message | None = None,
    ) -> Message | None:
        """Create Message instance using from_slack pattern."""
        if message_data.get("subtype") in {
            "channel_join",
            "channel_leave",
            "bot_message",
        } or not any(
            [
                message_data.get("text"),
                message_data.get("attachments"),
                message_data.get("files"),
                message_data.get("blocks"),
            ]
        ):
            return None

        try:
            if not (slack_user_id := (message_data.get("user") or message_data.get("bot_id"))):
                return None

            try:
                author = Member.objects.get(
                    slack_user_id=slack_user_id, workspace=conversation.workspace
                )
            except Member.DoesNotExist:
                author = None
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        time.sleep(delay)

                        user_info = client.users_info(user=slack_user_id)
                        self._handle_slack_response(user_info, "users_info")

                        author = Member.update_data(
                            user_info["user"], conversation.workspace, save=True
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f"Created new member: {slack_user_id}")
                        )
                        break
                    except SlackApiError as e:
                        if e.response["error"] == "ratelimited":
                            retry_after = int(
                                e.response.headers.get("Retry-After", delay * (retry_count + 1))
                            )

                            retry_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Rate limited on user info. Retrying after {retry_after}s"
                                )
                            )
                            time.sleep(retry_after)
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Failed to fetch user data for {slack_user_id}"
                                )
                            )
                            return None

                if not author:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Could not fetch user {slack_user_id}, skipping message"
                        )
                    )
                    return None

            return Message.update_data(
                data=message_data,
                conversation=conversation,
                author=author,
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
