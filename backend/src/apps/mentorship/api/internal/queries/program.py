"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.db.models import Q

from apps.common.utils import normalize_limit
from apps.mentorship.api.internal.graphql_errors import (
    AuthenticationRequiredError,
    ManagementProgramAccessDeniedError,
)
from apps.mentorship.api.internal.nodes.program import PaginatedPrograms, ProgramNode
from apps.mentorship.models import Program
from apps.mentorship.models.program_admin import ProgramAdmin
from apps.nest.api.internal.permissions import IsAuthenticated

PAGE_SIZE = 25
MAX_LIMIT = 1000
logger = logging.getLogger(__name__)


@strawberry.type
class ProgramQuery:
    """Program queries."""

    @strawberry.field
    def get_program(self, info: strawberry.Info, program_key: str) -> ProgramNode | None:
        """Get a program by Key."""
        try:
            program = Program.objects.prefetch_related(
                "admins__github_user", "admins__nest_user"
            ).get(key=program_key)
        except Program.DoesNotExist:
            msg = f"Program with key '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None

        if program.status != Program.ProgramStatus.PUBLISHED and not program.user_has_access(
            info.context.request.user
        ):
            return None

        return program

    @strawberry.field(name="managementProgram")
    def get_management_program(
        self, info: strawberry.Info, program_key: str
    ) -> ProgramNode | None:
        """Return program details for admins, mentors, or mentees.

        Sets ``user_role`` so the client can tailor the view without probing for
        access-denied errors.
        """
        user = info.context.request.user
        if not user.is_authenticated:
            raise AuthenticationRequiredError()  # noqa: RSE102
        try:
            program = Program.objects.prefetch_related(
                "admins__github_user", "admins__nest_user"
            ).get(key=program_key)
        except Program.DoesNotExist:
            msg = f"Program with key '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None

        role = program.get_user_role(user)
        if role is None:
            raise ManagementProgramAccessDeniedError()  # noqa: RSE102

        program.user_role = role
        return program

    @strawberry.field(permission_classes=[IsAuthenticated])
    def my_programs(
        self,
        info: strawberry.Info,
        search: str = "",
        page: int = 1,
        limit: int = 24,
    ) -> PaginatedPrograms:
        """Get paginated programs where the current user is admin, mentor, or mentee."""
        user = info.context.request.user
        github_user = getattr(user, "github_user", None)

        admin_program_ids = ProgramAdmin.objects.filter(admin__nest_user=user).values_list(
            "program_id", flat=True
        )

        mentor_q = Q(modules__mentors__nest_user=user)
        mentee_q = Q(modules__menteemodule__mentee__nest_user=user)
        if github_user is not None:
            mentor_q |= Q(modules__mentors__github_user=github_user)
            mentee_q |= Q(modules__menteemodule__mentee__github_user=github_user)

        query = Q(id__in=admin_program_ids) | mentor_q | mentee_q

        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            normalized_limit = PAGE_SIZE

        queryset = (
            Program.objects.prefetch_related(
                "admins__github_user",
                "admins__nest_user",
                "modules__mentors__github_user",
                "modules__mentors__nest_user",
            )
            .filter(query)
            .distinct()
        )

        if search:
            queryset = queryset.filter(name__icontains=search)

        total_count = queryset.count()
        total_pages = max(1, (total_count + normalized_limit - 1) // normalized_limit)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * normalized_limit

        paginated_programs = list(
            queryset.order_by("-nest_created_at")[offset : offset + normalized_limit]
        )

        # Determine each program's role in bulk (admin > mentor > mentee), scoped to
        # the current page — a fixed number of queries regardless of page size.
        page_ids = [program.id for program in paginated_programs]
        admin_ids = set(
            ProgramAdmin.objects.filter(
                admin__nest_user=user, program_id__in=page_ids
            ).values_list("program_id", flat=True)
        )
        mentor_ids = set(
            Program.objects.filter(mentor_q, id__in=page_ids).values_list("id", flat=True)
        )

        results = []
        for program in paginated_programs:
            if program.id in admin_ids:
                program.user_role = "admin"
            elif program.id in mentor_ids:
                program.user_role = "mentor"
            else:
                program.user_role = "mentee"
            results.append(program)

        return PaginatedPrograms(
            current_page=page,
            programs=results,
            total_pages=total_pages,
        )
