from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from apps.slack.models import Conversation, EntityChannel
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

ct = ContentType.objects.get_for_model(Chapter)

class Command(BaseCommand):
    help = 'Populate EntityChannel records for Chapters, Committees, and Projects based on Slack data.'

    def handle(self, *args, **options):
        from django.utils.text import slugify
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
                # If you add --workspace-id, filter here:
                # qs = qs.filter(workspace_id=options.get("workspace_id"))
                conversations = qs.filter(name__icontains=needle)
                for conv in conversations:
                    obj, was_created = EntityChannel.objects.get_or_create(
                        content_type=content_type,
                        object_id=entity.pk,
                        conversation=conv,
                        defaults={
                            "is_main_channel": False,
                            "is_reviewed": False,
                            "kind": "slack",
                        }
                    )
                    if was_created:
                        created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} EntityChannel records.'))
