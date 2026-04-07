"""Event signals."""

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.owasp.models.event import Event
from apps.owasp.utils.notifications import publish_event_notification

MEANINGFUL_FIELDS = (
    "name",
    "start_date",
    "end_date",
    "suggested_location",
    "url",
    "description",
)


@receiver(pre_save, sender=Event)
def event_pre_save(sender, instance, **kwargs):  # noqa: ARG001
    """Store the previous values before saving."""
    if instance.pk:
        db_instance = Event.objects.filter(pk=instance.pk).values(*MEANINGFUL_FIELDS).first()
        if db_instance:
            instance._previous_values = {  # noqa: SLF001
                field: db_instance.get(field) for field in MEANINGFUL_FIELDS
            }
    else:
        instance._previous_values = {}  # noqa: SLF001


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, **kwargs):  # noqa: ARG001
    """Signal handler for event creation and updates."""
    if created:
        transaction.on_commit(lambda inst=instance: publish_event_notification(inst, "created"))
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
                lambda inst=instance, cf=changed_fields: publish_event_notification(
                    inst, "updated", changed_fields=cf
                )
            )
