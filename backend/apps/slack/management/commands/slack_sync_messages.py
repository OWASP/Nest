"""A command to populate Slack messages data for all conversations."""

import logging
import os
import time
from datetime import UTC, datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile
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
        parser.add_argument(
            "--slack-user-id",
            type=str,
            help="Slack user ID to sync messages for",
        )
        parser.add_argument(
            "--github-user-id",
            type=str,
            help="GitHub user login to sync messages for (looks up Slack ID from profile)",
        )
        parser.add_argument(
            "--start-at",
            type=str,
            help="Start date for message range (YYYY-MM-DD, defaults to Jan 1 of current year)",
        )
        parser.add_argument(
            "--end-at",
            type=str,
            help="End date for message range (YYYY-MM-DD, defaults to today)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        channel_id = options["channel_id"]
        delay = options["delay"]
        max_retries = options["max_retries"]
        slack_user_id = options["slack_user_id"]
        github_user_id = options["github_user_id"]
        start_at = options["start_at"]
        end_at = options["end_at"]

        # Resolve Slack user ID if GitHub user ID is provided
        if github_user_id:
            slack_user_id = self._resolve_github_to_slack(github_user_id)
            if not slack_user_id:
                return

        # If slack_user_id is provided or resolved, use search-based sync
        if slack_user_id:
            self._sync_user_messages(
                user_id=slack_user_id,
                start_at=start_at,
                end_at=end_at,
                delay=delay,
                max_retries=max_retries,
            )
            return

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

    def _resolve_github_to_slack(self, github_login: str) -> str | None:
        """Resolve GitHub login to Slack user ID.

        Args:
            github_login: GitHub user login.

        Returns:
            Slack user ID or None if not found or not set.

        """
        self.stdout.write(f"Looking up Slack ID for GitHub user: {github_login}")

        try:
            github_user = User.objects.get(login=github_login)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"GitHub user not found: {github_login}\n"
                    f"Sync the user first with: python manage.py github_sync_user {github_login}"
                )
            )
            return None

        try:
            profile = MemberProfile.objects.get(github_user=github_user)
        except MemberProfile.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f"No OWASP profile found for GitHub user: {github_login}\n"
                    "Create a profile in Django admin first."
                )
            )
            return None

        if not profile.owasp_slack_id:
            self.stderr.write(
                self.style.ERROR(
                    f"No Slack ID set for GitHub user: {github_login}\n"
                    f"Update the profile with their Slack ID in Django admin, then try:\n"
                    f"  python manage.py slack_sync_messages --slack-user-id <SLACK_USER_ID>"
                )
            )
            return None

        self.stdout.write(self.style.SUCCESS(f"Resolved to Slack ID: {profile.owasp_slack_id}"))
        return profile.owasp_slack_id

    def _sync_user_messages(
        self,
        user_id: str,
        start_at: str | None,
        end_at: str | None,
        delay: float,
        max_retries: int,
    ):
        """Sync messages from a specific user using search API.

        Args:
            user_id: Slack user ID to search for.
            start_at: Start date (YYYY-MM-DD).
            end_at: End date (YYYY-MM-DD).
            delay: Delay between requests.
            max_retries: Max retry attempts.

        """
        # Parse dates
        today = datetime.now(UTC)
        current_year = today.year

        start_date = (
            datetime.strptime(start_at, "%Y-%m-%d").replace(tzinfo=UTC)
            if start_at
            else datetime(current_year, 1, 1, tzinfo=UTC)
        )
        end_date = datetime.strptime(end_at, "%Y-%m-%d").replace(tzinfo=UTC) if end_at else today

        self.stdout.write(
            f"\nSyncing messages for user {user_id} from {start_date.date()} to {end_date.date()}"
        )

        # Use user search token for search.messages API
        if not (search_token := os.environ.get("DJANGO_SLACK_SEARCH_TOKEN", "")):
            self.stderr.write(
                self.style.ERROR(
                    "DJANGO_SLACK_SEARCH_TOKEN environment variable is not set.\n"
                    "This should be a user token with search:read scope.\n"
                )
            )
            return

        client = WebClient(token=search_token)

        workspaces = Workspace.objects.all()
        if not workspaces.exists():
            self.stdout.write(self.style.WARNING("No workspaces found"))
            return

        total_messages = 0

        for workspace in workspaces:
            self.stdout.write(f"\nProcessing workspace: {workspace.name}")

            # Search for messages using search.messages API
            query = f"from:<@{user_id}>"
            page = 1
            retry_count = 0

            while True:
                try:
                    response = client.search_messages(
                        query=query,
                        count=100,
                        sort="timestamp",
                        sort_dir="desc",
                        page=page,
                    )

                    self._handle_slack_response(response, "search_messages")

                    messages_data = response.get("messages", {}).get("matches", [])
                    if not messages_data:
                        self.stdout.write(f"No more messages found for page {page}")
                        break

                    self.stdout.write(
                        f"  Processing {len(messages_data)} messages from page {page}"
                    )
                    logger.info("Processing %s messages from page %s", len(messages_data), page)

                    messages_to_save = []
                    should_stop = False

                    for message_data in messages_data:
                        # Parse message timestamp
                        ts = message_data.get("ts", "0")
                        message_time = datetime.fromtimestamp(float(ts), tz=UTC)

                        # Stop if message is older than start_date
                        if message_time < start_date:
                            self.stdout.write(
                                f"Reached messages older than {start_date.date()}, stopping"
                            )
                            should_stop = True
                            break

                        # Skip if message is newer than end_date
                        if message_time > end_date:
                            continue

                        # Get or create conversation
                        channel_id = message_data.get("channel", {}).get("id")
                        if not channel_id:
                            logger.warning("Message missing channel ID, skipping")
                            continue

                        conversation, _ = Conversation.objects.get_or_create(
                            slack_channel_id=channel_id,
                            workspace=workspace,
                            defaults={
                                "name": message_data.get("channel", {}).get("name", "unknown"),
                            },
                        )

                        # Create message - note: _create_message may return None if message
                        # already exists or fails validation
                        message = self._create_message(
                            client=client,
                            conversation=conversation,
                            delay=delay,
                            max_retries=max_retries,
                            message_data=message_data,
                        )

                        if message:
                            messages_to_save.append(message)
                            logger.debug("Created message %s for saving", ts)
                        else:
                            logger.warning("Message %s returned None from _create_message", ts)
                            self.stdout.write(f"    Skipped message {ts} (returned None)")

                    logger.info(
                        "Page %s: %s messages to save out of %s processed",
                        page,
                        len(messages_to_save),
                        len(messages_data),
                    )

                    if messages_to_save:
                        Message.bulk_save(messages_to_save)
                        total_messages += len(messages_to_save)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  Saved {len(messages_to_save)} messages from page {page}"
                            )
                        )
                        logger.info("Saved %s messages from page %s", len(messages_to_save), page)

                    if should_stop:
                        break

                    page += 1
                    time.sleep(delay)

                except SlackApiError as e:
                    if e.response["error"] == "ratelimited":
                        if retry_count >= max_retries:
                            self.stdout.write(
                                self.style.ERROR(f"Max retries ({max_retries}) exceeded")
                            )
                            break

                        retry_after = int(e.response.headers.get("Retry-After", delay))
                        retry_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"Rate limited. Retrying after {retry_after}s")
                        )
                        time.sleep(retry_after)
                        continue

                    self.stdout.write(
                        self.style.ERROR(f"Error searching messages: {e.response['error']}")
                    )
                    break

        self.stdout.write(
            self.style.SUCCESS(f"\nFinished! Total messages synced: {total_messages}")
        )

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
