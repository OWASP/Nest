"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from apps.mentorship.api.internal.nodes.program import ProgramNode
from apps.mentorship.models import Program
from apps.mentorship.models.mentor import Mentor

PAGE_SIZE = 25
logger = logging.getLogger(__name__)


@strawberry.type
class ProgramQuery:
    """Program queries."""

    @strawberry.field
    def program(self, program_key: str) -> ProgramNode:
        """Get a program by Key."""
        try:
            program = Program.objects.prefetch_related("admins__github_user").get(key=program_key)
        except Program.DoesNotExist as err:
            msg = f"Program with key '{program_key}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

        return program

    @strawberry.field
    def my_programs(
        self,
        info: strawberry.Info,
        username: str,
        search: str = "",
    ) -> list[ProgramNode]:
        """Get programs where user is either an admin or a mentor in modules."""
        try:
            # Get the mentor object for the given username
            mentor = Mentor.objects.select_related("github_user").get(
                github_user__login__iexact=username.strip().lower()
            )
        except Mentor.DoesNotExist:
            logger.warning("Mentor with username '%s' not found.", username)
            return []

        # Get programs where user is admin OR has modules as mentor
        programs_queryset = (
            Program.objects.prefetch_related(
                "admins__github_user", "modules__mentors__github_user"
            )
            .filter(
                Q(admins=mentor)  # User is program admin
                | Q(modules__mentors=mentor)  # User is mentor in any module of this program
            )
            .distinct()
        )

        # Apply search filter if provided
        if search:
            programs_queryset = programs_queryset.filter(name__icontains=search)

        # Add userRole to each program object
        programs_list = []
        for program in programs_queryset:
            # Determine user's role in this program
            is_admin = mentor in program.admins.all()

            # Priority: admin role takes precedence over mentor role
            program.user_role = "admin" if is_admin else "mentor"
            programs_list.append(program)

        # Sort by most recently created
        programs_list.sort(key=lambda x: x.nest_created_at, reverse=True)

        return programs_list
