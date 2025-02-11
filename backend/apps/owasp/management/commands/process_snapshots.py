import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from apps.owasp.models.snapshot import Snapshot
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.event import Event
from apps.owasp.models.project import Project

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process pending snapshots and populate them with new data'

    def handle(self, *args, **options):
        try:
            self.process_pending_snapshots()
        except Exception as e:
            logger.error(f"Error processing snapshots: {str(e)}")
            raise

    def process_pending_snapshots(self):
        pending_snapshots = Snapshot.objects.filter(status=Snapshot.Status.PENDING)
        
        if not pending_snapshots.exists():
            logger.info("No pending snapshots found")
            return

        for snapshot in pending_snapshots:
            try:
                with transaction.atomic():
                    self.process_single_snapshot(snapshot)
            except Exception as e:
                error_msg = f"Error processing snapshot {snapshot.id}: {str(e)}"
                logger.error(error_msg)
                snapshot.status = Snapshot.Status.ERROR
                snapshot.error_message = error_msg
                snapshot.save()

    def process_single_snapshot(self, snapshot):
        logger.info(f"Processing snapshot {snapshot.id} ({snapshot.start_at} to {snapshot.end_at})")
        
        # Update status to processing
        snapshot.status = Snapshot.Status.PROCESSING
        snapshot.save()

        try:
            # Fetch new data for each model type
            new_chapters = self.get_new_items(Chapter, snapshot)
            new_committees = self.get_new_items(Committee, snapshot)
            new_events = self.get_new_items(Event, snapshot)
            new_projects = self.get_new_items(Project, snapshot)

            # Add items to snapshot
            snapshot.new_chapters.add(*new_chapters)
            snapshot.new_committees.add(*new_committees)
            snapshot.new_events.add(*new_events)
            snapshot.new_projects.add(*new_projects)

            # Update status to completed
            snapshot.status = Snapshot.Status.COMPLETED
            snapshot.save()

            logger.info(f"Successfully processed snapshot {snapshot.id}")
            logger.info(f"Added: {new_chapters.count()} chapters, "
                       f"{new_committees.count()} committees, "
                       f"{new_events.count()} events, "
                       f"{new_projects.count()} projects")

        except Exception as e:
            raise Exception(f"Failed to process snapshot: {str(e)}")

    def get_new_items(self, model, snapshot):
        """Get items created or updated within the snapshot timeframe."""
        return model.objects.filter(
            Q(created_at__gte=snapshot.start_at, created_at__lte=snapshot.end_at) |
            Q(updated_at__gte=snapshot.start_at, updated_at__lte=snapshot.end_at)
        ) 