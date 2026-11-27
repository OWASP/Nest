"""A command to update context for OWASP project data."""

from django.db.models import QuerySet

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.project import extract_project_content
from apps.owasp.models.project import Project


class Command(BaseContextCommand):
    key_field_name = "key"
    model_class = Project

    def extract_content(self, entity: Project) -> tuple[str, str]:
        """Extract content from the project."""
        return extract_project_content(entity)

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with ordering."""
        return super().get_base_queryset()
