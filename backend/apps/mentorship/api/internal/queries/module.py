"""OWASP module GraphQL queries."""

import logging

import strawberry

from apps.mentorship.api.internal.nodes.module import ModuleNode
from apps.mentorship.models import Module

logger = logging.getLogger(__name__)


@strawberry.type
class ModuleQuery:
    """Module queries."""

    @strawberry.field
    def get_program_modules(self, program_key: str) -> list[ModuleNode]:
        """Get all modules by program Key. Returns an empty list if program is not found."""
        return (
            Module.objects.filter(program__key=program_key)
            .select_related("program", "project")
            .prefetch_related("mentors__github_user")
            .order_by("started_at")
        )

    @strawberry.field
    def get_project_modules(self, project_key: str) -> list[ModuleNode]:
        """Get all modules by project Key. Returns an empty list if project is not found."""
        return (
            Module.objects.filter(project__key=project_key)
            .select_related("program", "project")
            .prefetch_related("mentors__github_user")
            .order_by("started_at")
        )

    @strawberry.field
    def get_module(self, module_key: str, program_key: str) -> ModuleNode | None:
        """Get a single module by its key within a specific program."""
        try:
            return (
                Module.objects.select_related("program", "project")
                .prefetch_related("mentors__github_user")
                .get(key=module_key, program__key=program_key)
            )
        except Module.DoesNotExist:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None
