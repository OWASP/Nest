"""Command to sync Slack channels and groups from the OWASP Slack workspace."""

import logging
import time

from django.core.management.base import BaseCommand
from slack_sdk.errors import SlackApiError

from apps.slack.apps import SlackConfig
from apps.slack.models.conversation import Conversation

logger = logging.getLogger(__name__)


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
        # Parse command arguments
        batch_size = options["batch_size"]
        delay = options["delay"]
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Running in dry-run mode - no database changes will be made")
            )

        try:
            # Get Slack app instance
            app = SlackConfig.app
            if not app:
                logger.error("Slack app is not configured properly")
                self.stdout.write(self.style.ERROR("Slack app is not configured properly"))
                return

            # Collect conversations from API
            all_conversations = self._fetch_all_conversations(app, batch_size, delay)

            # Save conversations to database
            if not dry_run and all_conversations:
                self.stdout.write(f"Saving {len(all_conversations)} conversations to database...")
                saved_count = Conversation.bulk_save_from_slack(all_conversations)
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully synced {saved_count} Slack conversations")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Processed {len(all_conversations)} conversations (dry run)"
                    )
                )

        except SlackApiError as e:
            error_msg = f"Error calling Slack API: {e}"
            logger.exception(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
        except Exception as e:
            error_msg = f"Failed to sync Slack conversations: {e}"
            logger.exception(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))

    def _fetch_all_conversations(self, app, batch_size, delay):
        """Fetch all conversations from Slack API.

        Args:
        ----
            app: Slack app instance
            batch_size: Number of conversations to retrieve per request
            delay: Delay between API requests in seconds

        Returns:
        -------
            List of conversation data

        """
        all_conversations = []
        next_cursor = None
        total_processed = 0

        self.stdout.write("Fetching conversations from Slack API...")

        while True:
            # Fetch batch of conversations
            result = app.client.conversations_list(
                limit=batch_size,
                exclude_archived=False,
                types="public_channel,private_channel",
                cursor=next_cursor or None,
                timeout=30,
            )

            if not result.get("ok"):
                error = result.get("error", "Unknown error")
                logger.exception("Slack API error: %s", error)
                self.stdout.write(self.style.ERROR(f"Slack API error: {error}"))
                break

            batch_conversations = result.get("channels", [])
            total_processed += len(batch_conversations)

            # Display progress
            self.stdout.write(f"Processed {total_processed} conversations...")

            # Collect conversations
            if batch_conversations:
                all_conversations.extend(batch_conversations)

            # Handle pagination
            next_cursor = result.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break

            # Rate limiting protection
            if delay > 0:
                time.sleep(delay)

        self.stdout.write(f"Total conversations retrieved: {len(all_conversations)}")
        return all_conversations
