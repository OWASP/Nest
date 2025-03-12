"""OWASP app conversation models."""

import logging
from datetime import datetime, timezone

from django.db import models

from apps.common.models import BulkSaveModel, TimestampedModel

logger = logging.getLogger(__name__)


class Conversation(BulkSaveModel, TimestampedModel):
    """Model representing a Slack conversation (channel or group)."""

    class Meta:
        db_table = "slack_conversations"
        verbose_name_plural = "Conversations"

    entity_id = models.CharField(verbose_name="Entity ID", max_length=255, unique=True)
    name = models.CharField(verbose_name="Name", max_length=255)
    created_at = models.DateTimeField(verbose_name="Created At", blank=True, null=True)
    is_private = models.BooleanField(verbose_name="Is Private", default=False)
    is_archived = models.BooleanField(verbose_name="Is Archived", default=False)
    is_general = models.BooleanField(verbose_name="Is General", default=False)
    topic = models.TextField(verbose_name="Topic", blank=True, default="")
    purpose = models.TextField(verbose_name="Purpose", blank=True, default="")
    creator_id = models.CharField(verbose_name="Creator ID", max_length=255)

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

                if channel_id in entity_id_map:
                    # Update existing instance
                    instance = entity_id_map[channel_id]
                    for field, value in channel_data.items():
                        setattr(instance, field, value)
                    to_save.append(instance)
                else:
                    # Create new instance
                    new_conversation = cls(entity_id=channel_id, **channel_data)
                    to_save.append(new_conversation)

            except KeyError:
                logger.exception("Missing required field in conversation data")
                continue
            except Exception:
                logger.exception(
                    "Error processing conversation %s",
                    conversation.get("id", "unknown"),
                )
                continue

        return to_save

    @classmethod
    def bulk_save_from_slack(cls, conversations):
        """Bulk save conversations from Slack API data.

        Args:
        ----
            conversations: List of conversation data from Slack API

        Returns:
        -------
            int: Number of conversations saved

        """
        to_save = cls.prepare_from_slack_data(conversations)

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

        cls.bulk_save(cls, to_save, fields=update_fields)
        return len(to_save)
