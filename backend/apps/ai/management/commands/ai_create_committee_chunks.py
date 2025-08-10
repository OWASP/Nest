"""A command to create chunks of OWASP committee data for RAG."""

from django.db.models import Model

from apps.ai.common.base import BaseChunkCommand
from apps.ai.common.extractors.committee import extract_committee_content
from apps.owasp.models.committee import Committee


class Command(BaseChunkCommand):
    @property
    def model_class(self) -> type[Model]:
        return Committee

    @property
    def entity_name(self) -> str:
        return "committee"

    @property
    def entity_name_plural(self) -> str:
        return "committees"

    @property
    def key_field_name(self) -> str:
        return "key"

    def extract_content(self, entity: Committee) -> tuple[str, str]:
        """Extract content from the committee."""
        return extract_committee_content(entity)
