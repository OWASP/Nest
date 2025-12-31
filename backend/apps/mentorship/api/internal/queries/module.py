"""OWASP module GraphQL queries."""

import logging

import strawberry

from apps.mentorship.api.internal.nodes.module import ModuleNode
from apps.mentorship.models import Module
from apps.mentorship.models.program import Program

logger = logging.getLogger(__name__)


@strawberry.type
class ModuleQuery:
    """Module queries."""

    @strawberry.field
    def get_program_modules(self, program_key: str) -> list[ModuleNode]:
        """Get all modules by program Key.

        Returns an empty list if program is not found or if program is unpublished.
        Only returns modules from published programs for public access.
        """
        try:
            program = Program.objects.get(key=program_key)
            if program.status != Program.ProgramStatus.PUBLISHED:
                logger.warning(
                    "Attempted to access modules for unpublished program '%s' (status: %s)",
                    program_key,
                    program.status,
                )
                return []
        except Program.DoesNotExist:
            return []

        return (
            Module.objects.filter(program__key=program_key)
            .select_related("program", "project")
            .prefetch_related("mentors__github_user")
            .order_by("started_at")
        )

    @strawberry.field
    def get_project_modules(self, project_key: str) -> list[ModuleNode]:
        """Get all modules by project Key.

        Returns an empty list if project is not found.
        Only returns modules from published programs for public access.
        """
        return (
            Module.published_modules.filter(project__key=project_key)
            .select_related("program", "project")
            .prefetch_related("mentors__github_user")
            .order_by("started_at")
        )

    @strawberry.field
    def get_module(self, module_key: str, program_key: str) -> ModuleNode:
        """Get a single module by its key within a specific program."""
        try:
            program = Program.objects.get(key=program_key)
            if program.status != Program.ProgramStatus.PUBLISHED:
                msg = f"Module with key '{module_key}' under program '{program_key}' not found."
                logger.warning(
                    "Attempted to access module '%s' from unpublished program '%s' (status: %s)",
                    module_key,
                    program_key,
                    program.status,
                )
                raise ObjectDoesNotExist(msg)

            return (
                Module.objects.select_related("program", "project")
                .prefetch_related("mentors__github_user")
                .get(key=module_key, program__key=program_key)
            )
        except Module.DoesNotExist as err:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None
