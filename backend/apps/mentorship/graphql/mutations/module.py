"""Mentorship Module GraphQL Mutations."""

import strawberry

from apps.github.models import User as GithubUser
from apps.mentorship.graphql.nodes.modules import (
    CreateModuleInput,
    ModuleNode,
    UpdateModuleInput,
)
from apps.mentorship.models import Mentor, Module
from apps.mentorship.models.program import Program
from apps.mentorship.utils.user import get_authenticated_user
from apps.owasp.models import Project


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to module."""

    @strawberry.mutation
    def create_module(self, info: strawberry.Info, input_data: CreateModuleInput) -> ModuleNode:
        """Create a new mentorship module if the user is a admin."""
        request = info.context.request
        user = get_authenticated_user(request)

        try:
            program = Program.objects.get(id=input_data.program_id)
        except Program.DoesNotExist as err:
            raise Exception("Program not found") from err

        try:
            project = Project.objects.get(id=input_data.project_id)
        except Project.DoesNotExist as err:
            raise Exception("Project not found") from err

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            raise Exception("Only mentors can create modules") from err

        if admin not in program.admins.all():
            raise Exception("You must be an admin of this program to create a module")

        module = Module.objects.create(
            name=input_data.name,
            description=input_data.description or "",
            experience_level=input_data.experience_level.value,
            started_at=input_data.started_at or program.started_at,
            ended_at=input_data.ended_at or program.ended_at,
            domains=input_data.domains,
            tags=input_data.tags,
            program=program,
            project=project,
        )

        resolved_mentors = []
        for login in input_data.mentor_logins or []:
            try:
                github_user = GithubUser.objects.get(login=login)
            except GithubUser.DoesNotExist as err:
                raise Exception("GitHub username not found.") from err

            mentor_obj, _ = Mentor.objects.get_or_create(github_user=github_user)
            resolved_mentors.append(mentor_obj)

        module.mentors.set(resolved_mentors)

        return ModuleNode(
            id=module.id,
            name=module.name,
            description=module.description,
            domains=module.domains,
            ended_at=module.ended_at,
            experience_level=module.experience_level,
            mentors=list(module.mentors.all()),
            program=module.program,
            project_id=module.project.id if module.project else None,
            started_at=module.started_at,
            tags=module.tags,
        )

    @strawberry.mutation
    def update_module(self, info: strawberry.Info, input_data: UpdateModuleInput) -> ModuleNode:
        """Update an existing mentorship module. Only admins can update."""
        request = info.context.request
        user = get_authenticated_user(request)

        try:
            module = Module.objects.select_related("program").get(id=input_data.id)
        except Module.DoesNotExist as err:
            raise Exception("Module not found") from err

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            raise Exception("Only mentors can edit modules") from err

        if admin not in module.program.admins.all():
            raise Exception("You must be an admin of the module's program to edit it")

        if input_data.experience_level:
            module.experience_level = input_data.experience_level.value

        if input_data.project_id:
            try:
                project = Project.objects.get(id=input_data.project_id)
                module.project = project
            except Project.DoesNotExist as err:
                raise Exception("Project not found") from err

        update_fields = {
            "name": input_data.name,
            "description": input_data.description,
            "started_at": input_data.started_at,
            "ended_at": input_data.ended_at,
            "domains": input_data.domains,
            "tags": input_data.tags,
        }

        for field, value in update_fields.items():
            if value is not None:
                setattr(module, field, value)

        module.save()

        if input_data.mentor_logins is not None:
            resolved_mentors = []
            for login in input_data.mentor_logins:
                try:
                    github_user = GithubUser.objects.get(login=login)
                except GithubUser.DoesNotExist as err:
                    raise Exception("GitHub user not found") from err

                mentor_obj, _ = Mentor.objects.get_or_create(github_user=github_user)
                resolved_mentors.append(mentor_obj)

            module.mentors.set(resolved_mentors)

        return ModuleNode(
            id=module.id,
            name=module.name,
            description=module.description,
            domains=module.domains,
            ended_at=module.ended_at,
            experience_level=module.experience_level,
            mentors=list(module.mentors.all()),
            program=module.program,
            project_id=module.project.id if module.project else None,
            started_at=module.started_at,
            tags=module.tags,
        )
