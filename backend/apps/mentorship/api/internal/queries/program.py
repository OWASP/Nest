"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.db.models import Q

from apps.common.utils import normalize_limit
from apps.mentorship.api.internal.nodes.program import PaginatedPrograms, ProgramNode
from apps.mentorship.models import Program
from apps.mentorship.models.mentor import Mentor
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
            program = Program.objects.prefetch_related("admins__github_user").get(key=program_key)
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

        try:
            mentor = Mentor.objects.select_related("github_user").get(github_user=user.github_user)
        except Mentor.DoesNotExist:
            logger.warning("Mentor for user '%s' not found.", user.username)
            return PaginatedPrograms(programs=[], total_pages=0, current_page=page)

        if (normalized_limit := normalize_limit(limit, MAX_LIMIT)) is None:
            normalized_limit = PAGE_SIZE

        queryset = (
            Program.objects.prefetch_related(
                "admins__github_user", "modules__mentors__github_user"
            )
            .filter(Q(admins=mentor) | Q(modules__mentors=mentor))
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
        mentor_id = mentor.id
        for program in paginated_programs:
            is_admin = any(admin.id == mentor_id for admin in program.admins.all())
            program.user_role = "admin" if is_admin else "mentor"
            results.append(program)

        return PaginatedPrograms(
            programs=results,
            total_pages=total_pages,
            current_page=page,
        )
