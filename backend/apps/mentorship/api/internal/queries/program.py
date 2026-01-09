"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from apps.mentorship.api.internal.nodes.program import PaginatedPrograms, ProgramNode
from apps.mentorship.models import Program
from apps.mentorship.models.mentor import Mentor
from apps.nest.api.internal.permissions import IsAuthenticated

PAGE_SIZE = 25
logger = logging.getLogger(__name__)


@strawberry.type
class ProgramQuery:
    """Program queries."""

    @strawberry.field
    def get_program(self, info: strawberry.Info, program_key: str) -> ProgramNode:
        """Get a program by Key."""
        try:
            program = Program.objects.prefetch_related(
                "admins__github_user", "modules__mentors__github_user"
            ).get(key=program_key)

            if program.status == Program.ProgramStatus.PUBLISHED:
                return program

            user = getattr(info.context.request, "user", None)
            if user and user.is_authenticated:
                try:
                    mentor = Mentor.objects.get(github_user=user.github_user)
                    if program.admins.filter(id=mentor.id).exists():
                        logger.info(
                            "Admin '%s' accessing draft program '%s'",
                            user.username,
                            program_key,
                        )
                        return program

                    for module in program.modules.all():
                        if module.mentors.filter(id=mentor.id).exists():
                            logger.info(
                                "Mentor '%s' accessing draft program '%s'",
                                user.username,
                                program_key,
                            )
                            return program
                except Mentor.DoesNotExist:
                    pass

            msg = f"Program with key '{program_key}' not found."
            logger.warning(
                "Attempted public access to unpublished program '%s' (status: %s)",
                program_key,
                program.status,
            )
            raise ObjectDoesNotExist(msg)

        except Program.DoesNotExist as err:
            msg = f"Program with key '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

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
        total_pages = max(1, (total_count + limit - 1) // limit)
        page = max(1, min(page, total_pages))
        offset = (page - 1) * limit

        paginated_programs = queryset.order_by("-nest_created_at")[offset : offset + limit]

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
