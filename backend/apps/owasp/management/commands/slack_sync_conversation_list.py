"""Command to sync Slack channels and groups from the OWASP Slack workspace using slack-bolt."""

import logging
import time
from datetime import datetime, timezone
from functools import lru_cache

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from slack_bolt import App
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackSyncError(Exception):
    """Custom exception for Slack sync errors."""

    TOKEN_ERROR = "Slack token not available"  # noqa: S105
    API_ERROR_FORMAT = "Slack API error: {}"


@lru_cache(maxsize=1)
def get_slack_app():
    """Get or create a cached Slack app instance."""
    slack_token = getattr(settings, "SLACK_BOT_TOKEN", None)
    if not slack_token:
        raise SlackSyncError(SlackSyncError.TOKEN_ERROR)
    return App(token=slack_token)


def handle_api_error(error, error_message=None):
    """Handle API errors consistently."""
    message = error_message or f"Slack API error: {error}"
    logger.exception(message)
    raise SlackSyncError(SlackSyncError.API_ERROR_FORMAT.format(error)) from error


class Command(BaseCommand):
    """Django command to synchronize Slack conversations."""

    help = "Sync Slack channels and groups from the OWASP Slack workspace."

    def add_arguments(self, parser):
        """Define command line arguments."""
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of conversations to retrieve per request",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=0.1,
            help="Delay between API requests in seconds",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch conversations but don't update the database",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        from apps.slack.models.conversation import Conversation

        try:
            batch_size = options["batch_size"]
            delay = options["delay"]
            dry_run = options.get("dry_run", False)

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        "Running in dry-run mode - no database changes will be made"
                    )
                )

            count = self.sync_slack_conversations(
                Conversation,
                batch_size=batch_size,
                delay=delay,
                dry_run=dry_run,
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully synced {count} Slack conversations")
            )
        except Exception as e:
            error_msg = f"Failed to sync Slack conversations: {e}"
            logger.exception(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
            raise

    def sync_slack_conversations(
        self, conversation_model, batch_size=200, delay=0.1, dry_run=False
    ):
        """Synchronize Slack conversations with the database.

        Args:
        ----
            conversation_model: The Django model to store conversations
            batch_size: Number of conversations to retrieve per API call
            delay: Time in seconds to wait between API calls
            dry_run: If True, only fetch data without modifying the database

        Returns:
        -------
            int: Total number of conversations processed

        """
        app = get_slack_app()

        # Prepare for bulk operations
        existing_channels = {}
        if not dry_run:
            # Get existing conversations to minimize DB lookups
            existing_channels = {
                conv.entity_id: conv
                for conv in conversation_model.objects.all().only(
                    "entity_id",
                    "name",
                    "is_private",
                    "is_archived",
                    "is_general",
                    "topic",
                    "purpose",
                    "creator_id",
                )
            }

        # Track conversations to create or update
        to_create = []
        to_update = []

        # Pagination variables
        next_cursor = None
        total_processed = 0

        while True:
            try:
                # Fetch batch of conversations
                result = app.client.conversations_list(
                    limit=batch_size,
                    exclude_archived=False,
                    types="public_channel,private_channel",
                    cursor=next_cursor or None,
                )

                if not result.get("ok"):
                    error = result.get("error", "Unknown error")
                    handle_api_error(error)

                conversations = result.get("channels", [])

                # Process this batch
                if not dry_run:
                    new_creates, new_updates = self._prepare_conversation_changes(
                        conversations, conversation_model, existing_channels
                    )
                    to_create.extend(new_creates)
                    to_update.extend(new_updates)

                total_processed += len(conversations)
                self.stdout.write(f"Processed {len(conversations)} conversations...")

                # Handle pagination
                next_cursor = result.get("response_metadata", {}).get("next_cursor")
                if not next_cursor:
                    break

                # Rate limiting protection
                if delay > 0:
                    time.sleep(delay)

            except SlackApiError as e:
                handle_api_error(e, f"Error calling Slack API: {e}")
            except (ValueError, TypeError, ConnectionError) as e:
                handle_api_error(e, f"Unexpected error: {e}")

        # Perform bulk operations
        if not dry_run and (to_create or to_update):
            with transaction.atomic():
                if to_create:
                    conversation_model.objects.bulk_create(to_create)
                    logger.info("Bulk created %d conversations", len(to_create))  # G004 fix

                if to_update:
                    conversation_model.objects.bulk_update(
                        to_update,
                        [
                            "name",
                            "created_at",
                            "is_private",
                            "is_archived",
                            "is_general",
                            "topic",
                            "purpose",
                            "creator_id",
                        ],
                    )
                    logger.info("Bulk updated %d conversations", len(to_update))  # G004 fix

        return total_processed

    def _prepare_conversation_changes(self, conversations, conversation_model, existing_channels):
        """Prepare conversation objects for bulk create or update operations.

        Args:
        ----
            conversations: List of conversation data from Slack API
            conversation_model: Django model class for conversations
            existing_channels: Dict of existing conversations by entity_id

        Returns:
        -------
            Tuple of (objects_to_create, objects_to_update)

        """
        to_create = []
        to_update = []

        for conversation in conversations:
            try:
                channel_id = conversation.get("id")
                if not channel_id:
                    logger.warning("Found conversation without ID, skipping")
                    continue

                # Convert Unix timestamp to datetime
                created_timestamp = int(conversation.get("created", 0))
                created_datetime = datetime.fromtimestamp(created_timestamp, tz=timezone.utc)

                channel_data = {
                    "name": conversation.get("name", ""),
                    "created_at": created_datetime,
                    "is_private": conversation.get("is_private", False),
                    "is_archived": conversation.get("is_archived", False),
                    "is_general": conversation.get("is_general", False),
                    "topic": conversation.get("topic", {}).get("value", ""),
                    "purpose": conversation.get("purpose", {}).get("value", ""),
                    "creator_id": conversation.get("creator", ""),
                }

                if channel_id in existing_channels:
                    # Update existing
                    existing = existing_channels[channel_id]
                    changed = False
                    for field, value in channel_data.items():
                        if getattr(existing, field) != value:
                            setattr(existing, field, value)
                            changed = True

                    if changed:
                        to_update.append(existing)
                else:
                    # Create new
                    new_conversation = conversation_model(entity_id=channel_id, **channel_data)
                    to_create.append(new_conversation)

            except KeyError:
                logger.exception("Missing required field in conversation data")
                continue
            except Exception:  # pylint: disable=broad-except
                # TRY401 fix - remove exception object from logging call
                logger.exception(
                    "Error processing conversation %s",
                    conversation.get("id", "unknown"),
                )
                continue

        return to_create, to_update
