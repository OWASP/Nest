"""Command to sync Slack channels and groups from the OWASP Slack workspace using slack-bolt."""

import logging
import time

from django.core.management.base import BaseCommand
from django.db import transaction
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig

logger = logging.getLogger(__name__)


class SlackSyncError(Exception):
    """Custom exception for Slack sync errors."""

    APP_NOT_CONFIGURED = "Slack app is not configured properly"
    API_ERROR_FORMAT = "Slack API error: {}"


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
        # Use the app from SlackConfig instead of creating a new one
        app = SlackConfig.app

        if not app:
            error_msg = SlackSyncError.APP_NOT_CONFIGURED
            logger.error(error_msg)
            raise SlackSyncError(error_msg)

        # Pagination variables
        next_cursor = None
        total_processed = 0
        total_saved = 0

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

                total_processed += len(conversations)
                self.stdout.write(f"Processed {len(conversations)} conversations...")

                # Save conversations if not in dry-run mode
                if not dry_run and conversations:
                    with transaction.atomic():
                        saved = conversation_model.bulk_save_from_slack(conversations)
                        total_saved += saved
                        logger.info("Saved %d conversations", saved)

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

        if not dry_run:
            self.stdout.write(f"Saved {total_saved} conversations")

        return total_processed
