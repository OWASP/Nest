from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from apps.slack.models import Conversation, EntityChannel
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.committee import Committee
from apps.owasp.models.project import Project

class Command(BaseCommand):
    help = 'Populate EntityChannel records for Chapters, Committees, and Projects based on Slack data.'

    def handle(self, *args, **options):
        created = 0
        # Example: match by name, can be improved
        for model, app_label, model_name in [
            (Chapter, 'owasp', 'chapter'),
            (Committee, 'owasp', 'committee'),
            (Project, 'owasp', 'project'),
        ]:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            for entity in model.objects.all():
                # Example: match conversation by name
                conversations = Conversation.objects.filter(name__icontains=entity.name)
                for conv in conversations:
                    obj, was_created = EntityChannel.objects.get_or_create(
                        content_type=content_type,
                        object_id=entity.pk,
                        conversation=conv,
                        defaults={
                            'is_main_channel': False,
                            'is_reviewed': False,
                            'kind': 'slack',
                        }
                    )
                    if was_created:
                        created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} EntityChannel records.'))
