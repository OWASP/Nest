"""OWASP module GraphQL queries."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist

from apps.mentorship.api.internal.nodes.module import ModuleNode
from apps.mentorship.models import Module
from apps.mentorship.models.mentor import Mentor
from apps.mentorship.models.program import Program

logger = logging.getLogger(__name__)


def _is_program_admin_or_mentor(user, program) -> bool:
    """Check if user is an admin or mentor of the program."""
    if not user or not user.is_authenticated:
        return False

    if not user.github_user:
        return False

    from django.db.models import Q

    try:
        mentor = Mentor.objects.get(github_user=user.github_user)

        return Program.objects.filter(
            Q(id=program.id) & (Q(admins=mentor) | Q(modules__mentors=mentor))
        ).exists()

    except Mentor.DoesNotExist:
        return False


@strawberry.type
class ModuleQuery:
    """Module queries."""

    @strawberry.field
    def get_program_modules(self, info: strawberry.Info, program_key: str) -> list[ModuleNode]:
        """Get all modules by program Key."""
        try:
            program = Program.objects.prefetch_related("admins", "modules__mentors").get(
                key=program_key
            )

            if program.status == Program.ProgramStatus.PUBLISHED:
                return (
                    Module.objects.filter(program__key=program_key)
                    .select_related("program", "project")
                    .prefetch_related("mentors__github_user")
                    .order_by("started_at")
                )

            user = getattr(info.context.request, "user", None)
            if _is_program_admin_or_mentor(user, program):
                logger.info(
                    "Admin/mentor accessing modules for draft program '%s'",
                    program_key,
                )
                return (
                    Module.objects.filter(program__key=program_key)
                    .select_related("program", "project")
                    .prefetch_related("mentors__github_user")
                    .order_by("started_at")
                )

            msg = f"Program with key '{program_key}' not found."
            logger.warning(
                "Attempted to access modules for unpublished program '%s' (status: %s)",
                program_key,
                program.status,
            )
            raise ObjectDoesNotExist(msg)

        except Program.DoesNotExist:
            msg = f"Program with key '{program_key}' not found."
            raise ObjectDoesNotExist(msg) from None

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
    def get_module(self, info: strawberry.Info, module_key: str, program_key: str) -> ModuleNode:
        """Get a single module by its key within a specific program."""
        try:
            program = Program.objects.prefetch_related("admins", "modules__mentors").get(
                key=program_key
            )

            if program.status != Program.ProgramStatus.PUBLISHED:
                user = getattr(info.context.request, "user", None)
                if not _is_program_admin_or_mentor(user, program):
                    msg = (
                        f"Module with key '{module_key}' under program '{program_key}' not found."
                    )
                    logger.warning(
                        "Attempted to access module '%s' from unpublished program '%s'",
                        module_key,
                        program_key,
                    )
                    raise ObjectDoesNotExist(msg)

                logger.info(
                    "Admin/mentor accessing module '%s' from draft program '%s'",
                    module_key,
                    program_key,
                )

            return (
                Module.objects.select_related("program", "project")
                .prefetch_related("mentors__github_user")
                .get(key=module_key, program__key=program_key)
            )
        except Program.DoesNotExist as err:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err
        except Module.DoesNotExist as err:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err
