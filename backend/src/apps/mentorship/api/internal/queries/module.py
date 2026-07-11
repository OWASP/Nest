"""OWASP module GraphQL queries."""

import logging

import strawberry
from django.db.models import Prefetch, Q
from django.db.models.functions import Lower

from apps.mentorship.api.internal.graphql_errors import (
    AuthenticationRequiredError,
    ManagementProgramAccessDeniedError,
)
from apps.mentorship.api.internal.nodes.module import ModuleNode
from apps.mentorship.models import Mentor, Module, Program

logger = logging.getLogger(__name__)


@strawberry.type
class ModuleQuery:
    """Module queries."""

    @strawberry.field
    def get_program_modules(self, info: strawberry.Info, program_key: str) -> list[ModuleNode]:
        """Get all modules by program Key. Returns an empty list if program is not found."""
        try:
            program = Program.objects.get(key=program_key)
        except Program.DoesNotExist:
            return []

        if program.status != Program.ProgramStatus.PUBLISHED and not program.user_has_access(
            info.context.request.user
        ):
            return []

        return (
            Module.objects.filter(program=program)
            .select_related("program", "project")
            .prefetch_related(
                Prefetch(
                    "mentors",
                    queryset=Mentor.objects.select_related("github_user").order_by(
                        Lower("github_user__login")
                    ),
                )
            )
            .order_by("order", "started_at")
        )

    @strawberry.field(name="managementProgramModules")
    def get_management_program_modules(
        self, info: strawberry.Info, program_key: str
    ) -> list[ModuleNode]:
        """List modules for the management UI, scoped to the caller's role.

        Admins see every module; mentors see the modules they mentor; mentees see
        the modules they're enrolled in.
        """
        user = info.context.request.user
        if not user.is_authenticated:
            raise AuthenticationRequiredError()  # noqa: RSE102
        try:
            program = Program.objects.get(key=program_key)
        except Program.DoesNotExist:
            return []

        if not program.user_has_access(user):
            raise ManagementProgramAccessDeniedError()  # noqa: RSE102

        modules = Module.objects.filter(program=program)

        if not program.has_admin(user):
            github_user = getattr(user, "github_user", None)
            role_q = Q(mentors__nest_user=user) | Q(menteemodule__mentee__nest_user=user)
            if github_user is not None:
                role_q |= Q(mentors__github_user=github_user)
                role_q |= Q(menteemodule__mentee__github_user=github_user)
            modules = modules.filter(role_q)

        return (
            modules.select_related("program", "project")
            .prefetch_related(
                Prefetch(
                    "mentors",
                    queryset=Mentor.objects.select_related("github_user").order_by(
                        Lower("github_user__login")
                    ),
                )
            )
            .distinct()
            .order_by("order", "started_at")
        )

    @strawberry.field
    def get_project_modules(self, project_key: str) -> list[ModuleNode]:
        """Get all modules by project Key. Returns an empty list if project is not found."""
        return (
            Module.objects.filter(project__key=project_key)
            .select_related("program", "project")
            .prefetch_related(
                Prefetch(
                    "mentors",
                    queryset=Mentor.objects.select_related("github_user").order_by(
                        Lower("github_user__login")
                    ),
                )
            )
            .order_by("order", "started_at")
        )

    @strawberry.field
    def get_module(
        self, info: strawberry.Info, module_key: str, program_key: str
    ) -> ModuleNode | None:
        """Get a single module by its key within a specific program."""
        try:
            module = (
                Module.objects.select_related("program", "project")
                .prefetch_related(
                    Prefetch(
                        "mentors",
                        queryset=Mentor.objects.select_related("github_user").order_by(
                            Lower("github_user__login")
                        ),
                    )
                )
                .get(key=module_key, program__key=program_key)
            )
        except Module.DoesNotExist:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None

        if (
            module.program.status != Program.ProgramStatus.PUBLISHED
            and not module.program.user_has_access(info.context.request.user)
        ):
            return None

        return module

    @strawberry.field(name="managementModule")
    def get_management_module(
        self, info: strawberry.Info, module_key: str, program_key: str
    ) -> ModuleNode | None:
        """Single module for the management UI; open to admins, mentors, and mentees.

        Sets ``user_role`` so the client can render a management or read-only view
        without probing for access-denied errors.
        """
        user = info.context.request.user
        if not user.is_authenticated:
            raise AuthenticationRequiredError()  # noqa: RSE102
        try:
            module = (
                Module.objects.select_related("program", "project")
                .prefetch_related(
                    Prefetch(
                        "mentors",
                        queryset=Mentor.objects.select_related("github_user").order_by(
                            Lower("github_user__login")
                        ),
                    )
                )
                .get(key=module_key, program__key=program_key)
            )
        except Module.DoesNotExist:
            msg = f"Module with key '{module_key}' under program '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None

        roles = [
            ("admin", module.program.has_admin),
            ("mentor", module.has_mentor),
            ("mentee", module.has_mentee),
        ]

        for role, checker in roles:
            if checker(user):
                module.user_role = role
                break
        else:
            raise ManagementProgramAccessDeniedError()  # noqa: RSE102

        return module
