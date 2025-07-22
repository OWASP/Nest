"""OWASP program GraphQL queries."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist

from apps.mentorship.api.internal.nodes.program import PaginatedPrograms, ProgramNode
from apps.mentorship.models import Program

PAGE_SIZE = 25
logger = logging.getLogger(__name__)


@strawberry.type
class ProgramQuery:
    """Program queries."""

    @strawberry.field
    def all_programs(
        self,
        info: strawberry.Info,
        page: int = 1,
        search: str = "",
        mentor_username: str | None = None,
    ) -> PaginatedPrograms:
        """Get all programs with optional pagination, search, and mentor filtering."""
        queryset = Program.objects.prefetch_related("admins__github_user").all()

        if mentor_username:
            mentor_username = mentor_username.strip().lower()
            queryset = queryset.filter(admins__github_user__login__iexact=mentor_username)

        if search:
            queryset = queryset.filter(name__icontains=search)

        total_count = queryset.count()
        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE
        offset = (page - 1) * PAGE_SIZE

        programs_qs = queryset.order_by("-nest_created_at")[offset : offset + PAGE_SIZE]

        return PaginatedPrograms(
            total_pages=total_pages,
            current_page=page,
            programs=programs_qs,
        )

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
