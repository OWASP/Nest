"""A command to create chunks of OWASP project data for RAG."""

from django.db.models import Model, QuerySet

from apps.ai.common.base.chunk_command import BaseChunkCommand
from apps.ai.common.extractors.project import extract_project_content
from apps.owasp.models.project import Project


class Command(BaseChunkCommand):
    def entity_name(self) -> str:
        return "project"

    def entity_name_plural(self) -> str:
        return "projects"

    def extract_content(self, entity: Project) -> tuple[str, str]:
        """Extract content from the project."""
        return extract_project_content(entity)

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with ordering."""
        return super().get_base_queryset()

    def key_field_name(self) -> str:
        return "key"

    def model_class(self) -> type[Model]:
        return Project
