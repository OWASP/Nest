"""A command to update context for OWASP repository data."""

from django.db.models import QuerySet

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.common.extractors.repository import extract_repository_content
from apps.github.models.repository import Repository


class Command(BaseContextCommand):
    key_field_name = "key"
    model_class = Repository

    def __init__(self, *args, **kwargs):
        """Initialize command for repository."""
        super().__init__(*args, **kwargs)
        self.entity_name_plural = "repositories"

    def extract_content(self, entity: Repository) -> tuple[str, str]:
        """Extract content from the repository."""
        return extract_repository_content(entity)

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset with filtering for OWASP site repositories."""
        return (
            super()
            .get_base_queryset()
            .filter(
                is_owasp_site_repository=True,
                is_archived=False,
                is_empty=False,
            )
        )

    def get_default_queryset(self) -> QuerySet:
        """Override to avoid is_active filter since Repository doesn't have that field."""
        return self.get_base_queryset()

    def source_name(self) -> str:
        """Return the source name for context creation."""
        return "owasp_repository"
