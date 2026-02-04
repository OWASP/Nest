"""Snapshot signals."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.utils.notifications import publish_snapshot_notification


@receiver(post_save, sender=Snapshot)
def snapshot_published(sender, instance, created, **kwargs):  # noqa: ARG001
    """Signal handler for snapshot publication."""
    if instance.status == Snapshot.Status.COMPLETED:
        publish_snapshot_notification(instance)
