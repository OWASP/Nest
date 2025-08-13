"""A command to update context for OWASP committee data."""

from django.db.models import Model

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.committee import extract_committee_content
from apps.owasp.models.committee import Committee


class Command(BaseContextCommand):
    def entity_name(self) -> str:
        return "committee"

    def entity_name_plural(self) -> str:
        return "committees"

    def extract_content(self, entity: Committee) -> tuple[str, str]:
        """Extract content from the committee."""
        return extract_committee_content(entity)

    def key_field_name(self) -> str:
        return "key"

    def model_class(self) -> type[Model]:
        return Committee
