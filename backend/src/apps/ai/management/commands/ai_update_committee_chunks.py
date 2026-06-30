"""A command to create chunks of OWASP committee data for RAG."""

from apps.ai.common.base.chunk_command import BaseChunkCommand
from apps.ai.common.extractors.committee import extract_committee_content
from apps.owasp.models.committee import Committee


class Command(BaseChunkCommand):
    key_field_name = "key"
    model_class = Committee

    def extract_content(self, entity: Committee) -> tuple[str, str]:
        """Extract content from the committee."""
        return extract_committee_content(entity)
