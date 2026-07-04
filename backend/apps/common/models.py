"""Common app models."""

# ruff: noqa: SLF001 https://docs.astral.sh/ruff/rules/private-member-access/

from django.db import models

BATCH_SIZE = 1000


class BulkSaveModel(models.Model):
    """Base model for bulk save action."""

    class Meta:
        """Meta options for BulkSaveModel."""

        abstract = True

    @staticmethod
    def bulk_save(model, objects, fields=None) -> None:
        """Bulk save objects.

        Args:
            model (Model): The Django model class.
            objects (list): List of model instances to save.
            fields (list, optional): List of fields to update.

        """
        from django.utils import timezone

        has_created_at = any(f.name == "nest_created_at" for f in model._meta.fields)
        has_updated_at = any(f.name == "nest_updated_at" for f in model._meta.fields)

        create_objs = [o for o in objects if not o.id]
        if create_objs:
            if has_created_at or has_updated_at:
                now = timezone.now()
                for o in create_objs:
                    if has_created_at and not getattr(o, "nest_created_at", None):
                        o.nest_created_at = now
                    if has_updated_at and not getattr(o, "nest_updated_at", None):
                        o.nest_updated_at = now
            model.objects.bulk_create(create_objs, BATCH_SIZE)

        update_objs = [o for o in objects if o.id]
        if update_objs:
            if has_updated_at:
                now = timezone.now()
                for o in update_objs:
                    o.nest_updated_at = now
                if fields is not None:
                    fields = list(fields)
                    if "nest_updated_at" not in fields:
                        fields.append("nest_updated_at")

            model.objects.bulk_update(
                update_objs,
                fields=fields or [field.name for field in model._meta.fields if not field.primary_key],
                batch_size=BATCH_SIZE,
            )
        objects.clear()


class TimestampedModel(models.Model):
    """Base model with auto created_at and updated_at fields."""

    class Meta:
        """Meta options for TimestampedModel."""

        abstract = True

    nest_created_at = models.DateTimeField(auto_now_add=True)
    nest_updated_at = models.DateTimeField(auto_now=True)
