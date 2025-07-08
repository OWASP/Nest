"""Mentorship Module GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError

from apps.common.utils import slugify
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

logger = logging.getLogger(__name__)


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to module."""

    @strawberry.mutation
    def create_module(self, info: strawberry.Info, input_data: CreateModuleInput) -> ModuleNode:
        """Create a new mentorship module if the user is a admin."""
        request = info.context.request
        user = get_authenticated_user(request)
        try:
            program = Program.objects.get(key=input_data.program_key)
        except Program.DoesNotExist as e:
            msg = "Program not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from e

        try:
            project = Project.objects.get(id=input_data.project_id)
        except Project.DoesNotExist as e:
            msg = "Project with not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from e

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as e:
            msg = "Only mentors can create modules."
            logger.warning(
                "User '%s' attempted to create a module but is not a mentor.",
                user.email,
                exc_info=True,
            )
            raise PermissionDenied(msg) from e

        if admin not in program.admins.all():
            msg = "You must be an admin of this program to create a module."
            logger.warning(
                "Permission denied for user '%s' to create module in program '%s'.",
                user.email,
                program.key,
            )
            raise PermissionDenied(msg)

        if (
            input_data.ended_at is not None
            and input_data.started_at is not None
            and input_data.ended_at <= input_data.started_at
        ):
            msg = "End date must be after start date."
            logger.warning("Validation error creating module: %s", msg)
            raise ValidationError(msg)

        module = Module.objects.create(
            name=input_data.name,
            key=slugify(input_data.name),
            description=input_data.description or "",
            experience_level=input_data.experience_level.value,
            started_at=input_data.started_at or program.started_at,
            ended_at=input_data.ended_at or program.ended_at,
            domains=input_data.domains,
            tags=input_data.tags,
            program=program,
            project=project,
        )

        resolved_mentors = [admin]
        for login in input_data.mentor_logins or []:
            try:
                github_user = GithubUser.objects.get(login__iexact=login.lower())
            except GithubUser.DoesNotExist as e:
                msg = f"GitHub user '{login}' not found."
                logger.warning(msg, exc_info=True)
                raise ObjectDoesNotExist(msg) from e

            mentor_obj, _ = Mentor.objects.get_or_create(github_user=github_user)
            resolved_mentors.append(mentor_obj)

        module.mentors.set(resolved_mentors)

        return ModuleNode(
            id=module.id,
            key=module.key,
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
            module = Module.objects.select_related("program").get(key=input_data.key)
        except Module.DoesNotExist as e:
            msg = "Module not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from e

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as e:
            msg = "Only mentors can edit modules."
            logger.warning(
                "User '%s' attempted to edit a module but is not a mentor.",
                user.email,
                exc_info=True,
            )
            raise PermissionDenied(msg) from e

        if admin not in module.program.admins.all():
            msg = "You must be an admin of the module's program to edit it."
            logger.warning(
                "Permission denied for user '%s' to edit module '%s'",
                user.email,
                module.name,
            )
            raise PermissionDenied(msg)

        if (
            input_data.ended_at is not None
            and input_data.started_at is not None
            and input_data.ended_at <= input_data.started_at
        ):
            msg = "End date must be after start date."
            logger.warning("Validation error updating module '%s': %s", module.key, msg)
            raise ValidationError(msg)

        if input_data.experience_level:
            module.experience_level = input_data.experience_level.value

        if input_data.project_id:
            try:
                project = Project.objects.get(id=input_data.project_id)
                module.project = project
            except Project.DoesNotExist as e:
                msg = f"Project with id '{input_data.project_id}' not found."
                logger.warning(msg, exc_info=True)
                raise ObjectDoesNotExist(msg) from e

        update_fields = {
            "key": slugify(input_data.name),
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
                    github_user = GithubUser.objects.get(login__iexact=login.lower())
                except GithubUser.DoesNotExist as e:
                    msg = "GitHub user not found."
                    logger.warning(msg, exc_info=True)
                    raise ObjectDoesNotExist(msg) from e

                mentor_obj, _ = Mentor.objects.get_or_create(github_user=github_user)
                resolved_mentors.append(mentor_obj)

            module.mentors.set(resolved_mentors)

        return ModuleNode(
            id=module.id,
            key=module.key,
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
