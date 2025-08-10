"""A command to update context for OWASP project data."""

from django.db.models import Model, QuerySet

from apps.ai.common.base import BaseContextCommand
from apps.ai.common.extractors.project import extract_project_content
from apps.owasp.models.project import Project


class Command(BaseContextCommand):
    @property
    def model_class(self) -> type[Model]:
        return Project

    @property
    def entity_name(self) -> str:
        return "project"

    @property
    def entity_name_plural(self) -> str:
        return "projects"

    @property
    def key_field_name(self) -> str:
        return "key"

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with ordering."""
        return super().get_base_queryset()

    def extract_content(self, entity: Project) -> tuple[str, str]:
        """Extract content from the project."""
        return extract_project_content(entity)
