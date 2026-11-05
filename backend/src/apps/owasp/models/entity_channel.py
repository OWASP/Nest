"""Model for linking OWASP entities (chapter, committee, project) to communication channels."""

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class EntityChannel(models.Model):
    """Model representing a link between an entity and a channel."""

    class Platform(models.TextChoices):
        """Channel platform choices."""

        SLACK = "slack", "Slack"

    class Meta:
        """Model options."""

        db_table = "owasp_entity_channels"
        unique_together = (
            "channel_id",
            "channel_type",
            "entity_id",
            "entity_type",
        )
        verbose_name = "Entity channel"
        verbose_name_plural = "Entity channels"

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this channel is active",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Indicates if this is the main channel for the entity",
    )
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Indicates if the channel has been reviewed",
    )
    platform = models.CharField(
        max_length=5,
        default=Platform.SLACK,
        choices=Platform.choices,
        help_text="Platform of the channel (e.g., Slack)",
    )

    # GFKs.

    # Channel.
    channel = GenericForeignKey("channel_type", "channel_id")
    channel_id = models.PositiveBigIntegerField()
    channel_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="+",
    )

    # Entity.
    entity = GenericForeignKey("entity_type", "entity_id")
    entity_id = models.PositiveBigIntegerField()
    entity_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="+",
    )

    def __str__(self):
        """Return a readable string representation of the EntityChannel."""
        return f"{self.entity} - {self.channel} ({self.platform})"
