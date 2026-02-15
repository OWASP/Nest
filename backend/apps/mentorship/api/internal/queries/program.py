"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.db.models import Q

from apps.common.utils import normalize_limit
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
    def get_program(self, program_key: str) -> ProgramNode | None:
        """Get a program by Key."""
        try:
            program = Program.objects.prefetch_related(
                "admins__github_user", "admins__nest_user"
            ).get(key=program_key)
        except Program.DoesNotExist:
            msg = f"Program with key '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            return None

        return program

    @strawberry.field(permission_classes=[IsAuthenticated])
    def my_programs(
        self,
        info: strawberry.Info,
        search: str = "",
        page: int = 1,
        limit: int = 24,
    ) -> PaginatedPrograms:
        """Get paginated programs where the current user is admin or mentor."""
        user = info.context.request.user

        admin_program_ids = ProgramAdmin.objects.filter(admin__nest_user=user).values_list(
            "program_id", flat=True
        )

        query = Q(id__in=admin_program_ids)
        if user.github_user:
            query |= Q(modules__mentors__github_user=user.github_user)

        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            normalized_limit = PAGE_SIZE

        queryset = (
            Program.objects.prefetch_related(
                "admins__github_user",
                "admins__nest_user",
                "modules__mentors__github_user",
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

        paginated_programs = queryset.order_by("-nest_created_at")[
            offset : offset + normalized_limit
        ]

        results = []
        for program in paginated_programs:
            is_admin = any(admin.nest_user_id == user.id for admin in program.admins.all())
            program.user_role = "admin" if is_admin else "mentor"
            results.append(program)

        return PaginatedPrograms(
            current_page=page,
            programs=results,
            total_pages=total_pages,
        )
