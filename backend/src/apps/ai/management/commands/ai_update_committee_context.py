"""A command to update context for OWASP committee data."""

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.committee import extract_committee_content
from apps.owasp.models.committee import Committee


class Command(BaseContextCommand):
    key_field_name = "key"
    model_class = Committee

    def extract_content(self, entity: Committee) -> tuple[str, str]:
        """Extract content from the committee."""
        return extract_committee_content(entity)
