"""Command to sync Slack channels and groups from the OWASP Slack workspace."""

import logging
import time
from datetime import datetime, timezone

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)


class SlackSyncError(Exception):
    """Custom exception for Slack sync errors."""

    MISSING_TOKEN_ERROR = "SLACK BOT TOKEN not found in settings"  # noqa: S105
    API_ERROR_FORMAT = "Slack API error: {}"


class Command(BaseCommand):
    help = "Sync Slack channels and groups from the OWASP Slack workspace."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=200,
            help="Number of conversations to retrieve per request",
        )
        parser.add_argument(
            "--delay", type=float, default=0.5, help="Delay between API requests in seconds"
        )

    def handle(self, *args, **options):
        from apps.owasp.models.conversation import Conversation

        try:
            batch_size = options["batch_size"]
            delay = options["delay"]

            count = self.sync_slack_conversations(Conversation, batch_size=batch_size, delay=delay)

            self.stdout.write(
                self.style.SUCCESS(f"Successfully synced {count} Slack conversations")
            )
        except Exception as e:
            error_msg = f"Failed to sync Slack conversations: {e}"
            logger.exception(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
            raise

    def sync_slack_conversations(self, conversation_model, batch_size=200, delay=0.5):
        slack_token = getattr(settings, "SLACK_BOT_TOKEN", None)
        if not slack_token:
            raise SlackSyncError(SlackSyncError.MISSING_TOKEN_ERROR)

        url = "https://slack.com/api/conversations.list"
        params = {
            "limit": batch_size,
            "exclude_archived": False,
            "types": "public_channel,private_channel",
        }
        headers = {"Authorization": f"Bearer {slack_token}"}

        next_cursor = None
        total_processed = 0

        while True:
            if next_cursor:
                params["cursor"] = next_cursor

            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()

            if not data.get("ok"):
                error_msg = f"Slack API error: {data.get('error', 'Unknown error')}"
                logger.error(error_msg)
                raise SlackSyncError(error_msg)

            conversations = data.get("channels", [])
            self.process_conversations(conversations, conversation_model)
            total_processed += len(conversations)

            self.stdout.write(f"Processed {len(conversations)} conversations...")

            next_cursor = data.get("response_metadata", {}).get("next_cursor")
            if not next_cursor:
                break

            # Add a small delay to avoid rate limiting
            time.sleep(delay)

        return total_processed

    @transaction.atomic
    def process_conversations(self, conversations, conversation_model):
        conversation_objects = []

        for conversation in conversations:
            try:
                # Convert Unix timestamp to datetime
                created_timestamp = int(conversation.get("created", 0))
                created_datetime = datetime.fromtimestamp(created_timestamp, tz=timezone.utc)

                defaults = {
                    "name": conversation.get("name", ""),
                    "created_at": created_datetime,
                    "is_private": conversation.get("is_private", False),
                    "is_archived": conversation.get("is_archived", False),
                    "is_general": conversation.get("is_general", False),
                    "topic": conversation.get("topic", {}).get("value", ""),
                    "purpose": conversation.get("purpose", {}).get("value", ""),
                    "creator_id": conversation.get("creator", ""),
                }

                obj, created = conversation_model.objects.update_or_create(
                    entity_id=conversation["id"], defaults=defaults
                )
                conversation_objects.append(obj)

                if created:
                    logger.info("Created new conversation: %s", obj.name)
                else:
                    logger.info("Updated conversation: %s", obj.name)

            except KeyError:
                logger.exception("Missing required field in conversation data")
                continue
            except Exception:
                logger.exception(
                    "Error processing conversation %s", conversation.get("id", "unknown")
                )
                continue

        return conversation_objects
