"""Snapshot signals."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.utils.notifications import publish_snapshot_notification


@receiver(post_save, sender=Snapshot)
def snapshot_published(sender, instance, created, **kwargs):
    """Signal handler for snapshot publication."""
    print(f"Signal fired for Snapshot {instance.id}, Status: {instance.status}")
    if instance.status == Snapshot.Status.COMPLETED:
        print(f"Publishing notification for Snapshot {instance.id}")
        publish_snapshot_notification(instance)
