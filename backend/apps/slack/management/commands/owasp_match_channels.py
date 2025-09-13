"""A command to populate EntityChannel records from Slack data."""

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project
from apps.slack.models import Conversation, EntityChannel


class Command(BaseCommand):
    help = "Populate EntityChannel links for Chapters, Committees, and Projects."

    def handle(self, *args, **options):
        created = 0
        for model in (Chapter, Committee, Project):
            content_type = ContentType.objects.get_for_model(model)
            # Use .only and .iterator for memory efficiency
            for entity in model.objects.all().only("id", "name").iterator():
                # Normalize the name for matching (e.g., "OWASP Lima" -> "owasp-lima")
                needle = slugify(entity.name or "")
                if not needle:
                    continue
                qs = Conversation.objects.all()
                conversations = qs.filter(name__icontains=needle)
                for conv in conversations:
                    _, was_created = EntityChannel.objects.get_or_create(
                        entity_id=entity.pk,
                        entity_type=content_type,
                        channel_id=conv.pk,
                        channel_type=ContentType.objects.get_for_model(Conversation),
                        defaults={
                            "is_default": False,
                            "is_reviewed": False,
                            "platform": EntityChannel.Platform.SLACK,
                        },
                    )
                    if was_created:
                        created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} EntityChannel records."))
