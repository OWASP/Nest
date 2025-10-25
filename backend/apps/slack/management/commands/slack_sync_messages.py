"""A command to populate Slack messages data for all conversations."""

import logging
import os
import time
from datetime import UTC, datetime

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
        start_date, end_date = self._parse_date_range(start_at, end_at)
        
        self.stdout.write(
            f"\nSyncing messages for user {user_id} from {start_date.date()} to {end_date.date()}"
        )

        search_token = self._get_search_token()
        if not search_token:
            return

        client = WebClient(token=search_token)
        workspaces = self._get_workspaces()
        if not workspaces:
            return

        total_messages = 0
        for workspace in workspaces:
            workspace_messages = self._sync_workspace_messages(
                workspace, user_id, start_date, end_date, client, delay, max_retries
            )
            total_messages += workspace_messages

        self.stdout.write(
            self.style.SUCCESS(f"\nFinished! Total messages synced: {total_messages}")
        )

    def _parse_date_range(self, start_at: str | None, end_at: str | None) -> tuple[datetime, datetime]:
        """Parse start and end dates with defaults."""
        today = datetime.now(UTC)
        current_year = today.year

        start_date = (
            datetime.strptime(start_at, "%Y-%m-%d").replace(tzinfo=UTC)
            if start_at
            else datetime(current_year, 1, 1, tzinfo=UTC)
        )
        end_date = datetime.strptime(end_at, "%Y-%m-%d").replace(tzinfo=UTC) if end_at else today
        
        return start_date, end_date

    def _get_search_token(self) -> str | None:
        """Get and validate search token."""
        search_token = os.environ.get("DJANGO_SLACK_SEARCH_TOKEN", "")
        if not search_token:
            self.stderr.write(
                self.style.ERROR(
                    "DJANGO_SLACK_SEARCH_TOKEN environment variable is not set.\n"
                    "This should be a user token with search:read scope.\n"
                )
            )
            return None
        return search_token

    def _get_workspaces(self):
        """Get workspaces with validation."""
        workspaces = Workspace.objects.all()
        if not workspaces.exists():
            self.stdout.write(self.style.WARNING("No workspaces found"))
            return None
        return workspaces

    def _sync_workspace_messages(
        self,
        workspace,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        client: WebClient,
        delay: float,
        max_retries: int,
    ) -> int:
        """Sync messages for a single workspace."""
        self.stdout.write(f"\nProcessing workspace: {workspace.name}")
        
        query = f"from:<@{user_id}>"
        page = 1
        retry_count = 0
        total_saved = 0

        while True:
            response = self._search_messages_with_retry(
                client, query, page, retry_count, max_retries, delay
            )
            if response is None:  # Failed after retries
                break
            elif response == "retry":  # Need to retry
                retry_count += 1
                continue
            
            # Handle successful response
            retry_count = 0  # Reset retry count on success
            messages_data = response.get("messages", {}).get("matches", [])
            
            if not messages_data:
                self.stdout.write(f"No more messages found for page {page}")
                break

            self.stdout.write(f"  Processing {len(messages_data)} messages from page {page}")
            logger.info("Processing %s messages from page %s", len(messages_data), page)

            messages_saved, should_stop = self._process_message_batch(
                messages_data, workspace, start_date, end_date, client, delay, max_retries, page
            )
            total_saved += messages_saved
            
            if should_stop:
                break

            page += 1
            time.sleep(delay)

        return total_saved

    def _search_messages_with_retry(
        self, client: WebClient, query: str, page: int, retry_count: int, max_retries: int, delay: float
    ):
        """Search messages with retry logic for rate limiting."""
        try:
            response = client.search_messages(
                query=query,
                count=100,
                sort="timestamp",
                sort_dir="desc",
                page=page,
            )
            self._handle_slack_response(response, "search_messages")
            return response
            
        except SlackApiError as e:
            return self._handle_search_error(e, retry_count, max_retries, delay)

    def _handle_search_error(self, error: SlackApiError, retry_count: int, max_retries: int, delay: float):
        """Handle search API errors with appropriate retry logic."""
        if error.response["error"] == "ratelimited":
            if retry_count >= max_retries:
                self.stdout.write(
                    self.style.ERROR(f"Max retries ({max_retries}) exceeded")
                )
                return None

            retry_after = int(error.response.headers.get("Retry-After", delay))
            self.stdout.write(
                self.style.WARNING(f"Rate limited. Retrying after {retry_after}s")
            )
            time.sleep(retry_after)
            return "retry"  # Signal to retry

        self.stdout.write(
            self.style.ERROR(f"Error searching messages: {error.response['error']}")
        )
        return None

    def _process_message_batch(
        self,
        messages_data: list,
        workspace,
        start_date: datetime,
        end_date: datetime,
        client: WebClient,
        delay: float,
        max_retries: int,
        page: int,
    ) -> tuple[int, bool]:
        """Process a batch of messages and return (saved_count, should_stop)."""
        messages_to_save = []
        should_stop = False

        for message_data in messages_data:
            if not self._is_valid_message_data(message_data):
                continue
                
            message_time = self._get_message_timestamp(message_data)
            
            # Check date range with early returns
            if message_time < start_date:
                self.stdout.write(
                    f"Reached messages older than {start_date.date()}, stopping"
                )
                should_stop = True
                break
                
            if not self._is_message_in_date_range(message_time, start_date, end_date):
                continue

            processed_message = self._process_single_message(
                message_data, workspace, client, delay, max_retries
            )
            
            if processed_message:
                messages_to_save.append(processed_message)
                logger.debug("Created message %s for saving", message_data.get("ts", "0"))
            else:
                ts = message_data.get("ts", "0")
                logger.warning("Message %s returned None from _create_message", ts)
                self.stdout.write(f"    Skipped message {ts} (returned None)")

        # Save messages if any were processed
        saved_count = self._save_message_batch(messages_to_save, page)
        
        return saved_count, should_stop

    def _is_valid_message_data(self, message_data: dict) -> bool:
        """Validate message data has required fields."""
        return bool(message_data.get("ts"))

    def _get_message_timestamp(self, message_data: dict) -> datetime:
        """Extract timestamp from message data."""
        ts = message_data.get("ts", "0")
        return datetime.fromtimestamp(float(ts), tz=UTC)

    def _is_message_in_date_range(self, message_time: datetime, start_date: datetime, end_date: datetime) -> bool:
        """Check if message is within the specified date range."""
        return start_date <= message_time <= end_date

    def _process_single_message(
        self, message_data: dict, workspace, client: WebClient, delay: float, max_retries: int
    ):
        """Process a single message and return the created Message object or None."""
        channel_id = message_data.get("channel", {}).get("id")
        if not channel_id:
            logger.warning("Message missing channel ID, skipping")
            return None

        conversation = self._get_or_create_conversation(message_data, workspace, channel_id)
        
        return self._create_message(
            client=client,
            conversation=conversation,
            delay=delay,
            max_retries=max_retries,
            message_data=message_data,
        )

    def _get_or_create_conversation(self, message_data: dict, workspace, channel_id: str):
        """Get or create conversation for the message."""
        conversation, _ = Conversation.objects.get_or_create(
            slack_channel_id=channel_id,
            workspace=workspace,
            defaults={
                "name": message_data.get("channel", {}).get("name", "unknown"),
            },
        )
        return conversation

    def _save_message_batch(self, messages_to_save: list, page: int) -> int:
        """Save a batch of messages and return count saved."""
        if not messages_to_save:
            return 0
            
        Message.bulk_save(messages_to_save)
        saved_count = len(messages_to_save)
        
        self.stdout.write(
            self.style.SUCCESS(f"  Saved {saved_count} messages from page {page}")
        )
        logger.info("Saved %s messages from page %s", saved_count, page)
        
        logger.info(
            "Page %s: %s messages to save out of %s processed",
            page,
            saved_count,
            len(messages_to_save),
        )
        
        return saved_count

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
        try:
            replies = self._fetch_all_reply_pages(client, message, delay, max_retries)
            self._save_replies(replies, message)
        except SlackApiError as e:
            self._handle_fetch_replies_error(e, message)

    def _fetch_all_reply_pages(
        self, 
        client: WebClient, 
        message: Message, 
        delay: float, 
        max_retries: int
    ) -> list[Message]:
        """Fetch all pages of replies for a message."""
        replies = []
        cursor = None
        has_more = True
        
        while has_more:
            page_replies, cursor, has_more = self._fetch_reply_page(
                client, message, cursor, delay, max_retries
            )
            if page_replies is None:  # Error occurred
                break
            replies.extend(page_replies)
            
        return replies

    def _fetch_reply_page(
        self, 
        client: WebClient, 
        message: Message, 
        cursor: str | None, 
        delay: float, 
        max_retries: int
    ) -> tuple[list[Message] | None, str | None, bool]:
        """Fetch a single page of replies. Returns (replies, next_cursor, has_more)."""
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                response = self._get_replies_response(client, message, cursor)
                return self._process_replies_response(response, client, message, delay, max_retries)
                
            except SlackApiError as e:
                if not self._handle_reply_fetch_error(e, retry_count, max_retries, delay):
                    return None, None, False
                retry_count += 1
                
        return None, None, False

    def _get_replies_response(self, client: WebClient, message: Message, cursor: str | None):
        """Get replies response from Slack API."""
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
        return response

    def _process_replies_response(
        self, 
        response: dict, 
        client: WebClient, 
        message: Message, 
        delay: float, 
        max_retries: int
    ) -> tuple[list[Message], str | None, bool]:
        """Process the API response and create reply Message objects."""
        messages = response.get("messages", [])
        if not messages:
            return [], None, False

        replies = [
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
        
        return replies, cursor, has_more

    def _handle_reply_fetch_error(
        self, 
        error: SlackApiError, 
        retry_count: int, 
        max_retries: int, 
        delay: float
    ) -> bool:
        """Handle errors during reply fetching. Returns True if should retry."""
        if error.response["error"] != "ratelimited":
            raise error  # Re-raise non-rate-limit errors
            
        if retry_count >= max_retries:
            self.stdout.write(
                self.style.ERROR(
                    f"Max retries ({max_retries}) exceeded for thread"
                )
            )
            return False

        retry_after = int(
            error.response.headers.get("Retry-After", delay * (retry_count + 1))
        )
        self.stdout.write(
            self.style.WARNING(
                f"Rate limited. Retrying after {retry_after} seconds"
            )
        )
        time.sleep(retry_after)
        return True

    def _handle_fetch_replies_error(self, error: SlackApiError, message: Message):
        """Handle top-level errors when fetching replies."""
        self.stdout.write(
            self.style.ERROR(
                f"Failed to fetch thread replies for message {message.url}:"
                f" {error.response['error']}"
            )
        )

    def _save_replies(self, replies: list[Message], message: Message):
        """Save replies to database if any exist."""
        if not (replies_count := len(replies)):
            return
            
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
        author = self._get_or_create_message_author(
            client, message_data, conversation, delay, max_retries
        )

        return Message.update_data(
            data=message_data,
            conversation=conversation,
            author=author,
            parent_message=parent_message,
            save=False,
        )

    def _get_or_create_message_author(
        self,
        client: WebClient,
        message_data: dict,
        conversation: Conversation,
        delay: float,
        max_retries: int,
    ) -> Member | None:
        """Get or create the author (Member) for a message."""
        slack_user_id = message_data.get("user") or message_data.get("bot_id")
        if not slack_user_id:
            return None

        # Try to get existing member first
        author = self._get_existing_member(slack_user_id, conversation.workspace)
        if author:
            return author

        # Create new member if not found
        return self._create_new_member(
            client, message_data, slack_user_id, conversation.workspace, delay, max_retries
        )

    def _get_existing_member(self, slack_user_id: str, workspace) -> Member | None:
        """Try to get existing member from database."""
        try:
            return Member.objects.get(
                slack_user_id=slack_user_id,
                workspace=workspace,
            )
        except Member.DoesNotExist:
            return None

    def _create_new_member(
        self,
        client: WebClient,
        message_data: dict,
        slack_user_id: str,
        workspace,
        delay: float,
        max_retries: int,
    ) -> Member | None:
        """Create a new member (user or bot) with retry logic."""
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if message_data.get("user"):
                    return self._create_user_member(client, slack_user_id, workspace)
                else:
                    return self._create_bot_member(client, slack_user_id, workspace)
                    
            except SlackApiError as e:
                if not self._handle_member_creation_error(e, retry_count, max_retries, delay, slack_user_id):
                    break
                retry_count += 1
                
        return None

    def _create_user_member(self, client: WebClient, slack_user_id: str, workspace) -> Member:
        """Create a user member from Slack API data."""
        user_info = client.users_info(user=slack_user_id)
        self._handle_slack_response(user_info, "users_info")

        author = Member.update_data(
            user_info["user"], workspace, save=True
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created a new member: {slack_user_id}")
        )
        return author

    def _create_bot_member(self, client: WebClient, slack_user_id: str, workspace) -> Member:
        """Create a bot member from Slack API data."""
        bot_info = client.bots_info(bot=slack_user_id)
        self._handle_slack_response(bot_info, "bots_info")
        
        bot_data = {
            "id": slack_user_id,
            "is_bot": True,
            "name": bot_info["bot"].get("name"),
            "real_name": bot_info["bot"].get("name"),
        }
        
        author = Member.update_data(
            bot_data, workspace, save=True
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created bot member: {slack_user_id}")
        )
        return author

    def _handle_member_creation_error(
        self, 
        error: SlackApiError, 
        retry_count: int, 
        max_retries: int, 
        delay: float, 
        slack_user_id: str
    ) -> bool:
        """Handle errors during member creation. Returns True if should retry."""
        if error.response.get("error") == "ratelimited":
            if retry_count >= max_retries:
                return False
                
            retry_after = int(error.response.headers.get("Retry-After", delay))
            self.stdout.write(self.style.WARNING("Rate limited on member info"))
            time.sleep(retry_after)
            return True
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch member data for {slack_user_id}"
                )
            )
            return False

    def _handle_slack_response(self, response, api_method):
        """Handle Slack API response and raise exception if needed."""
        if not response["ok"]:
            error_message = f"{api_method} API call failed"
            logger.error(error_message)
            self.stdout.write(self.style.ERROR(error_message))
