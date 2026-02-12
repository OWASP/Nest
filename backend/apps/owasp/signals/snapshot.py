"""Snapshot signals."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.utils.notifications import publish_snapshot_notification


@receiver(pre_save, sender=Snapshot)
def snapshot_pre_save(sender, instance, **kwargs):  # noqa: ARG001
    """Store the previous status before saving."""
    if instance.pk:
        instance._previous_status = (  # noqa: SLF001
            Snapshot.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        )
    else:
        instance._previous_status = None  # noqa: SLF001


@receiver(post_save, sender=Snapshot)
def snapshot_published(sender, instance, created, **kwargs):  # noqa: ARG001
    """Signal handler for snapshot publication."""
    if instance.status == Snapshot.Status.COMPLETED and (
        created or instance._previous_status != Snapshot.Status.COMPLETED  # noqa: SLF001
    ):
        publish_snapshot_notification(instance)
