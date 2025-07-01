"""A command to populate Slack messages data for all conversations."""

import logging
import time

from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize
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
            default=999,
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
                else Conversation.objects.filter(sync_messages=True, workspace=workspace)
            )

            for conversation in conversations:
                self._fetch_conversation(
                    batch_size=batch_size,
                    client=client,
                    conversation=conversation,
                    delay=delay,
                    include_replies=True,
                    max_retries=max_retries,
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
            self._fetch_messages(
                batch_size=batch_size,
                client=client,
                conversation=conversation,
                delay=delay,
                include_replies=include_replies,
                max_retries=max_retries,
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

    def _fetch_messages(
        self,
        batch_size: int,
        client: WebClient,
        conversation: Conversation,
        delay: float,
        max_retries: int,
        *,
        include_replies: bool = True,
    ) -> None:
        """Fetch all parent messages (non-thread) for a conversation."""
        cursor = None
        has_more = True
        while has_more:
            try:
                retry_count = 0
                response = client.conversations_history(
                    channel=conversation.slack_channel_id,
                    cursor=cursor,
                    limit=batch_size,
                    oldest=(
                        latest_message.ts
                        if (latest_message := conversation.latest_message)
                        else "0"
                    ),
                )
                self._handle_slack_response(response, "conversations_history")

                messages = [
                    message
                    for message_data in response.get("messages", [])
                    if (
                        message := self._create_message(
                            client=client,
                            conversation=conversation,
                            delay=delay,
                            max_retries=max_retries,
                            message_data=message_data,
                        )
                    )
                ]
                cursor = response.get("response_metadata", {}).get("next_cursor")
                has_more = bool(cursor)
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

            Message.bulk_save(messages.copy())
            if include_replies and messages:
                print("Fetching message replies...")
                for message in messages:
                    if not message.has_replies:
                        continue

                    self._fetch_replies(
                        client=client,
                        message=message,
                        delay=delay,
                        max_retries=max_retries,
                    )

    def _fetch_replies(
        self,
        client: WebClient,
        message: Message,
        delay: float,
        max_retries: int,
    ):
        """Fetch all thread replies for parent messages."""
        replies = []
        try:
            cursor = None
            has_more = True
            while has_more:
                retry_count = 0
                try:
                    params = {
                        "channel": message.conversation.slack_channel_id,
                        "cursor": cursor,
                        "inclusive": False,
                        "limit": 1000,
                        "oldest": (
                            latest_reply.ts if (latest_reply := message.latest_reply) else "0"
                        ),
                        "ts": message.slack_message_id,
                    }
                    response = client.conversations_replies(**params)
                    self._handle_slack_response(response, "conversations_replies")

                    messages = response.get("messages", [])
                    if not messages:
                        break

                    replies += [
                        reply
                        for reply_data in messages
                        if (
                            reply := self._create_message(
                                client=client,
                                conversation=message.conversation,
                                delay=delay,
                                max_retries=max_retries,
                                message_data=reply_data,
                                parent_message=message,
                            )
                        )
                    ]

                    cursor = response.get("response_metadata", {}).get("next_cursor")
                    has_more = bool(cursor)
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
                    f"Failed to fetch thread replies for message {message.url}:"
                    f" {e.response['error']}"
                )
            )

        if replies_count := len(replies):
            print(
                f"Saving {replies_count} repl{pluralize(replies_count, 'y,ies')} for {message.url}"
            )
            Message.bulk_save(replies)

    def _create_message(
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
        author = None
        slack_user_id = message_data.get("user") or message_data.get("bot_id")
        if slack_user_id:
            try:
                author = Member.objects.get(
                    slack_user_id=slack_user_id,
                    workspace=conversation.workspace,
                )
            except Member.DoesNotExist:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        # User.
                        if message_data.get("user"):
                            user_info = client.users_info(user=slack_user_id)
                            self._handle_slack_response(user_info, "users_info")

                            author = Member.update_data(
                                user_info["user"], conversation.workspace, save=True
                            )
                            self.stdout.write(
                                self.style.SUCCESS(f"Created a new member: {slack_user_id}")
                            )
                        # Bot.
                        else:
                            bot_info = client.bots_info(bot=slack_user_id)
                            self._handle_slack_response(bot_info, "bots_info")
                            bot_data = {
                                "id": slack_user_id,
                                "is_bot": True,
                                "name": bot_info["bot"].get("name"),
                                "real_name": bot_info["bot"].get("name"),
                            }
                            author = Member.update_data(
                                bot_data, conversation.workspace, save=True
                            )
                            self.stdout.write(
                                self.style.SUCCESS(f"Created bot member: {slack_user_id}")
                            )
                        break
                    except SlackApiError as e:
                        if e.response.get("error") == "ratelimited":
                            retry_after = int(e.response.headers.get("Retry-After", delay))
                            retry_count += 1
                            self.stdout.write(self.style.WARNING("Rate limited on member info"))
                            time.sleep(retry_after)
                        else:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Failed to fetch member data for {slack_user_id}"
                                )
                            )
                            break

        return Message.update_data(
            data=message_data,
            conversation=conversation,
            author=author,
            parent_message=parent_message,
            save=False,
        )

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
