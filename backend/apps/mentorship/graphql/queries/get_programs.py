import strawberry
from apps.mentorship.models import Program
from apps.mentorship.graphql.nodes.program import PaginatedPrograms, ProgramNode

PAGE_SIZE = 20


@strawberry.type
class ProgramQuery:
    @strawberry.field
    def all_programs(self, page: int = 1, search: str = "") -> PaginatedPrograms:
        queryset = Program.objects.all()

        if search:
            queryset = queryset.filter(name__icontains=search)

        total_count = queryset.count()
        total_pages = (total_count + PAGE_SIZE - 1) // PAGE_SIZE
        offset = (page - 1) * PAGE_SIZE

        programs_qs = queryset.order_by("-nest_created_at")[offset : offset + PAGE_SIZE]

        programs = [
            ProgramNode(
                id=str(program.id),
                name=program.name,
                description=program.description,
                status=program.status,
                started_at=program.started_at,
                ended_at=program.ended_at,
            )
            for program in programs_qs
        ]

        return PaginatedPrograms(
            total_pages=total_pages, current_page=page, programs=programs
        )

    @strawberry.field
    def program(self, id: strawberry.ID) -> ProgramNode:
        try:
            program = Program.objects.get(id=id)
        except Program.DoesNotExist:
            raise Exception("Program not found")

        return ProgramNode(
            id=str(program.id),
            name=program.name,
            description=program.description,
            status=program.status,
            experience_levels=program.experience_levels,
            mentees_limit=program.mentees_limit,
            started_at=program.started_at,
            ended_at=program.ended_at,
            domains=program.domains,
            tags=program.tags,
            admins=program.admins.all(),
        )
