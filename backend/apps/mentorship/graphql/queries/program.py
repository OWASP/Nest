"""OWASP program GraphQL queries."""

import strawberry

from apps.mentorship.graphql.nodes.enum import ExperienceLevelEnum, ProgramStatusEnum
from apps.mentorship.graphql.nodes.program import PaginatedPrograms, ProgramNode
from apps.mentorship.models import Program

PAGE_SIZE = 25


@strawberry.type
class ProgramQuery:
    """Program queries."""

    @strawberry.field
    def all_programs(
        self,
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

        programs = [
            ProgramNode(
                id=program.id,
                key=program.key,
                name=program.name,
                description=program.description,
                admins=list(program.admins.all()),
                domains=program.domains,
                ended_at=program.ended_at,
                experience_levels=(
                    [ExperienceLevelEnum(level) for level in program.experience_levels]
                    if program.experience_levels
                    else []
                ),
                mentees_limit=program.mentees_limit,
                started_at=program.started_at,
                status=ProgramStatusEnum(program.status),
                tags=program.tags,
            )
            for program in programs_qs
        ]

        return PaginatedPrograms(
            total_pages=total_pages,
            current_page=page,
            programs=programs,
        )

    @strawberry.field
    def program(self, program_key: str) -> ProgramNode:
        """Get a program by ID."""
        try:
            program = Program.objects.prefetch_related("admins__github_user").get(key=program_key)
        except Program.DoesNotExist as err:
            raise Exception("Program not found") from err

        return ProgramNode(
            id=program.id,
            key=program.key,
            name=program.name,
            description=program.description,
            admins=list(program.admins.all()),
            domains=program.domains,
            ended_at=program.ended_at,
            experience_levels=(
                [ExperienceLevelEnum(level) for level in program.experience_levels]
                if program.experience_levels
                else []
            ),
            mentees_limit=program.mentees_limit,
            started_at=program.started_at,
            status=ProgramStatusEnum(program.status),
            tags=program.tags,
        )
