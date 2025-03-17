"""Slack app conversation model."""

import logging
from datetime import datetime, timezone

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel

logger = logging.getLogger(__name__)


class Conversation(BulkSaveModel, TimestampedModel):
    """conversation model."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    created_at = models.DateTimeField(verbose_name="Created At", blank=True, null=True)
    creator_id = models.CharField(verbose_name="Creator ID", max_length=255)
    entity_id = models.CharField(verbose_name="Entity ID", max_length=255, unique=True)
    is_archived = models.BooleanField(verbose_name="Is Archived", default=False)
    is_general = models.BooleanField(verbose_name="Is General", default=False)
    is_private = models.BooleanField(verbose_name="Is Private", default=False)
    name = models.CharField(verbose_name="Name", max_length=255)
    purpose = models.TextField(verbose_name="Purpose", blank=True, default="")
    topic = models.TextField(verbose_name="Topic", blank=True, default="")

    def __str__(self):
        """Return a string representation of the conversation."""
        return self.name

    @classmethod
    def prepare_from_slack_data(cls, conversations):
        """Prepare conversation objects from Slack API data.

        Args:
        ----
            conversations: List of conversation data from Slack API

        Returns:
        -------
            List of conversation objects to save

        """
        logger.info("Preparing %d conversations from Slack data", len(conversations))

        to_save = []
        entity_id_map = {
            conv.entity_id: conv
            for conv in cls.objects.all().only(
                "id",
                "entity_id",
                "name",
                "created_at",
                "is_private",
                "is_archived",
                "is_general",
                "topic",
                "purpose",
                "creator_id",
            )
        }

        logger.info("Found %d existing conversations in database", len(entity_id_map))

        to_update = 0
        to_create = 0
        skipped = 0
        errors = 0

        for conversation in conversations:
            try:
                channel_id = conversation.get("id")
                if not channel_id:
                    logger.warning("Found conversation without ID, skipping")
                    skipped += 1
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

                if channel_id in entity_id_map:
                    # Update existing instance
                    instance = entity_id_map[channel_id]
                    for field, value in channel_data.items():
                        setattr(instance, field, value)
                    to_save.append(instance)
                    to_update += 1
                    logger.debug(
                        "Updating existing conversation: %s - %s",
                        channel_id,
                        channel_data["name"],
                    )
                else:
                    # Create new instance
                    new_conversation = cls(entity_id=channel_id, **channel_data)
                    to_save.append(new_conversation)
                    to_create += 1
                    logger.debug(
                        "Creating new conversation: %s - %s",
                        channel_id,
                        channel_data["name"],
                    )

            except KeyError:
                logger.exception("Missing required field in conversation data")
                logger.exception("Conversation data: %s", conversation)
                skipped += 1
                errors += 1
                continue
            except Exception:
                logger.exception(
                    "Error processing conversation %s",
                    conversation.get("id", "unknown"),
                )
                skipped += 1
                errors += 1
                continue

        logger.info(
            "Prepared %d conversations to update and %d to create, skipped %d, "
            "encountered %d errors",
            to_update,
            to_create,
            skipped,
            errors,
        )

        return to_save

    @staticmethod
    def bulk_save(conversations, fields=None):
        """Bulk save conversations."""
        BulkSaveModel.bulk_save(Conversation, conversations, fields=fields)

    @classmethod
    def bulk_save_from_slack(cls, conversations):
        """Bulk save conversations from Slack API data."""
        logger.info("Starting bulk save from Slack for %d conversations", len(conversations))
        to_save = cls.prepare_from_slack_data(conversations)
        logger.info("Prepared %d conversations for saving", len(to_save))

        if not to_save:
            logger.warning("No conversations to save after preparation")
            return 0

        update_fields = [
            "name",
            "created_at",
            "is_private",
            "is_archived",
            "is_general",
            "topic",
            "purpose",
            "creator_id",
        ]

        # Save the count before the list is cleared
        saved_count = len(to_save)

        # Use the static method instead of calling BulkSaveModel directly
        cls.bulk_save(to_save, fields=update_fields)

        logger.info("Saved %d conversations", saved_count)
        return saved_count
