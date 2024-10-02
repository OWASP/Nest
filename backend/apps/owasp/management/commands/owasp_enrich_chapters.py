"""A command to enrich OWASP chapters with extra data."""

import logging
import time

from django.core.management.base import BaseCommand

from apps.owasp.models.chapter import Chapter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich OWASP chapters with extra data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        active_chapters = Chapter.active_chapters.order_by("id")
        active_chapters_count = active_chapters.count()

        chapters = []
        offset = options["offset"]
        for idx, chapter in enumerate(active_chapters[offset:]):
            prefix = f"{idx + offset + 1} of {active_chapters_count}"
            print(f"{prefix:<10} {chapter.owasp_url}")
            try:
                chapter.generate_geo_location()
                time.sleep(5)
            except Exception:
                logger.exception(
                    "Could not get geo data for chapter",
                    extra={"url": chapter.owasp_url},
                )

            chapters.append(chapter)

        Chapter.bulk_save(chapters, fields=("latitude", "longitude"))
