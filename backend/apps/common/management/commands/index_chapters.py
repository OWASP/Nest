"""A command to index chapters to Typesense."""

import typesense
from django.core.management.base import BaseCommand

from apps.common.typesense_client import chapters_schema, client
from apps.owasp.models.chapter import Chapter


class Command(BaseCommand):
    help = "Index chapters to Typesense"

    def handle(self, *args, **kwargs):
        try:
            client.collections["chapters"].delete()
            self.stdout.write(self.style.SUCCESS("Chapters collection deleted successfully."))
        except typesense.exceptions.ObjectNotFound:
            self.stdout.write(self.style.WARNING("Chapters collection does not exist."))

        client.collections.create(chapters_schema)
        self.stdout.write(self.style.SUCCESS("Chapters collection created successfully."))

        chapters = Chapter.objects.all()
        documents = [self.prepare_document(chapter) for chapter in chapters]

        client.collections["chapters"].documents.import_(documents, {"action": "create"})
        self.stdout.write(self.style.SUCCESS(f"Indexed {len(documents)} chapters into Typesense."))

    def prepare_document(self, chapter):
        return {
            "id": str(chapter.id),
            "name": chapter.name,
            "country": chapter.country,
            "region": chapter.region,
            "postal_code": chapter.postal_code,
            "location": [chapter.latitude, chapter.longitude]
            if chapter.latitude is not None and chapter.longitude is not None
            else None,
            "suggested_location": chapter.suggested_location,
            "meetup_group": chapter.meetup_group,
            "created_at": int(chapter.created_at.timestamp()) if chapter.created_at else 0,
            "updated_at": int(chapter.updated_at.timestamp()) if chapter.updated_at else 0,
        }
