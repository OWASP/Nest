"""A command to update context for OWASP chapter data."""

from django.db.models import Model

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.chapter import extract_chapter_content
from apps.owasp.models.chapter import Chapter


class Command(BaseContextCommand):
    def entity_name(self) -> str:
        return "chapter"

    def entity_name_plural(self) -> str:
        return "chapters"

    def extract_content(self, entity: Chapter) -> tuple[str, str]:
        """Extract content from the chapter."""
        return extract_chapter_content(entity)

    def key_field_name(self) -> str:
        return "key"

    def model_class(self) -> type[Model]:
        return Chapter
