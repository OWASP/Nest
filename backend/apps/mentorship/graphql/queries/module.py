"""OWASP module GraphQL queries."""

import strawberry

from apps.mentorship.graphql.nodes.modules import ModuleNode
from apps.mentorship.models import Module, Program
from apps.owasp.models import Project


@strawberry.type
class ModuleQuery:
    """Module queries."""

    @strawberry.field
    def modules_by_program(self, program_id: strawberry.ID) -> list[ModuleNode]:
        """Get all modules by program Id."""
        try:
            program = Program.objects.get(id=program_id)
        except Program.DoesNotExist as err:
            raise Exception("Program not found") from err

        modules = (
            Module.objects.filter(program=program)
            .select_related("project")
            .prefetch_related("mentors__github_user")
        )

        return [
            ModuleNode(
                id=module.id,
                name=module.name,
                description=module.description,
                domains=module.domains,
                ended_at=module.ended_at,
                experience_level=module.experience_level,
                mentors=list(module.mentors.all()),
                program=module.program,
                started_at=module.started_at,
                tags=module.tags,
            )
            for module in modules
        ]

    @strawberry.field
    def modules_by_project(self, project_id: strawberry.ID) -> list[ModuleNode]:
        """Get all modules by project Id."""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist as err:
            raise Exception("Project not found") from err

        modules = (
            Module.objects.filter(project=project)
            .select_related("program")
            .prefetch_related("mentors__github_user")
        )

        return [
            ModuleNode(
                id=module.id,
                name=module.name,
                description=module.description,
                domains=module.domains,
                ended_at=module.ended_at,
                experience_level=module.experience_level,
                mentors=list(module.mentors.all()),
                program=module.program,
                started_at=module.started_at,
                tags=module.tags,
            )
            for module in modules
        ]

    @strawberry.field
    def get_module(self, module_id: strawberry.ID) -> ModuleNode:
        """Get module by module Id."""
        try:
            module = (
                Module.objects.select_related("program", "project")
                .prefetch_related("mentors__github_user")
                .get(id=module_id)
            )
        except Module.DoesNotExist as err:
            raise Exception("Module not found") from err

        return ModuleNode(
            id=module.id,
            name=module.name,
            description=module.description,
            domains=module.domains,
            ended_at=module.ended_at,
            experience_level=module.experience_level,
            mentors=list(module.mentors.all()),
            program=module.program,
            started_at=module.started_at,
            tags=module.tags,
        )
