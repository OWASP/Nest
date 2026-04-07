"""Chapter signals."""

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.owasp.models.chapter import Chapter
from apps.owasp.utils.notifications import publish_chapter_notification

MEANINGFUL_FIELDS = ("name", "country", "region", "suggested_location", "description")


@receiver(pre_save, sender=Chapter)
def chapter_pre_save(sender, instance, **kwargs):  # noqa: ARG001
    """Store the previous values before saving."""
    if instance.pk:
        db_instance = Chapter.objects.filter(pk=instance.pk).values(*MEANINGFUL_FIELDS).first()
        if db_instance:
            instance._previous_values = {  # noqa: SLF001
                field: db_instance.get(field) for field in MEANINGFUL_FIELDS
            }
    else:
        instance._previous_values = {}  # noqa: SLF001


@receiver(post_save, sender=Chapter)
def chapter_post_save(sender, instance, created, **kwargs):  # noqa: ARG001
    """Signal handler for chapter creation and updates."""
    if created:
        transaction.on_commit(lambda: publish_chapter_notification(instance, "created"))
    else:
        changed_fields = {}
        previous_values = getattr(instance, "_previous_values", {})
        for field in MEANINGFUL_FIELDS:
            old_value = previous_values.get(field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changed_fields[field] = {
                    "old": str(old_value) if old_value is not None else None,
                    "new": str(new_value) if new_value is not None else None,
                }

        if changed_fields:
            transaction.on_commit(
                lambda: publish_chapter_notification(instance, "updated", changed_fields)
            )
