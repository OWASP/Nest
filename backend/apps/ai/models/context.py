"""AI app context model."""

import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.common.models import TimestampedModel
from apps.common.utils import truncate

logger = logging.getLogger(__name__)
SOURCE_MAX_LENGTH = 100


class Context(TimestampedModel):
    """Context model for storing generated text related to OWASP entities."""

    content = models.TextField(verbose_name="Generated Text")
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField()
    entity = GenericForeignKey("entity_type", "entity_id")
    source = models.CharField(
        max_length=SOURCE_MAX_LENGTH, blank=True, default="")

    class Meta:
        db_table = "ai_contexts"
        verbose_name = "Context"
        unique_together = ("entity_type", "entity_id")

    def __str__(self):
        """Human readable representation."""
        entity = (
            getattr(self.entity, "name", None)
            or getattr(self.entity, "key", None)
            or str(self.entity)
        )
        return f"{self.entity_type.model} {entity}: {truncate(self.content, 50)}"

    @staticmethod
    def update_data(
        content: str,
        entity,
        source: str = "",
        *,
        save: bool = True,
    ) -> "Context":
        """Create or update context for a given entity."""
        entity_type = ContentType.objects.get_for_model(entity)
        entity_id = entity.pk

        try:
            context = Context.objects.get(entity_type=entity_type, entity_id=entity_id)
        except Context.DoesNotExist:
            context = Context(entity_type=entity_type, entity_id=entity_id)

        context.content = content
        context.source = source

        if save:
            context.save()

        return context
