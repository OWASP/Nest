"""A command to update context for OWASP chapter data."""

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.chapter import extract_chapter_content
from apps.owasp.models.chapter import Chapter


class Command(BaseContextCommand):
    key_field_name = "key"
    model_class = Chapter

    def extract_content(self, entity: Chapter) -> tuple[str, str]:
        """Extract content from the chapter."""
        return extract_chapter_content(entity)
