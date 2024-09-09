"""Common app models."""

from django.db import models


class BulkSaveModel(models.Model):
    """Base model for bulk save action."""

    class Meta:
        abstract = True

    @staticmethod
    def bulk_save(model, objects):
        """Bulk save objects."""
        model.objects.bulk_create(o for o in objects if not o.id)
        model.objects.bulk_update(
            (o for o in objects if o.id),
            fields=[field.name for field in model._meta.fields if not field.primary_key],  # noqa: SLF001
        )
        objects.clear()


class TimestampedModel(models.Model):
    """Base model with auto created_at and updated_at fields."""

    class Meta:
        abstract = True

    nest_created_at = models.DateTimeField(auto_now_add=True)
    nest_updated_at = models.DateTimeField(auto_now=True)
