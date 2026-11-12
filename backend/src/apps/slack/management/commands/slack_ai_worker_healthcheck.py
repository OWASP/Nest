"""Check the local AI queue worker heartbeat for ECS."""

import socket
from datetime import timedelta

import django_rq
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from rq import Worker


class Command(BaseCommand):
    """Check an AI worker on this host, including idle workers."""

    def handle(self, *args, **options):
        """Fail when no local worker has a recent heartbeat."""
        # Staging workers use --worker-ttl 90; allow 30 seconds for probe jitter.
        oldest_heartbeat = timezone.now() - timedelta(seconds=120)
        for worker in Worker.all(queue=django_rq.get_queue("ai")):
            if (
                worker.hostname == socket.gethostname()
                and worker.last_heartbeat is not None
                and worker.last_heartbeat >= oldest_heartbeat
            ):
                return
        message = "No healthy local AI queue worker"
        raise CommandError(message)
