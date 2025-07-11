"""Mentorship Module GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction

from apps.common.utils import slugify
from apps.github.models import User as GithubUser
from apps.mentorship.graphql.nodes.module import (
    CreateModuleInput,
    ModuleNode,
    UpdateModuleInput,
)
from apps.mentorship.models import Mentor, Module, Program
from apps.mentorship.utils.user import get_user_entities_by_github_username
from apps.nest.graphql.permissions import IsAuthenticated
from apps.owasp.models import Project

logger = logging.getLogger(__name__)


def _resolve_mentors_from_logins(logins: list[str]) -> set[Mentor]:
    """Resolve a list of GitHub logins to a set of Mentor objects."""
    mentors = set()
    for login in logins:
        try:
            github_user = GithubUser.objects.get(login__iexact=login.lower())
            mentor, _ = Mentor.objects.get_or_create(github_user=github_user)
            mentors.add(mentor)
        except GithubUser.DoesNotExist as e:
            # Using ValueError for invalid input, as it's a standard Python/Django pattern.
            msg = f"GitHub user '{login}' not found."
            logger.warning(msg, exc_info=True)
            raise ValueError(msg) from e
    return mentors


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to module."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_module(self, info: strawberry.Info, input_data: CreateModuleInput) -> ModuleNode:
        """Create a new mentorship module. User must be an admin of the program."""
        username = info.context.request.user
        user_entities = get_user_entities_by_github_username(username)

        if not user_entities:
            msg = "Logic error: Authenticated user not found in the database."
            raise ObjectDoesNotExist(msg)

        github_user, user = user_entities
        try:
            program = Program.objects.get(key=input_data.program_key)
            project = Project.objects.get(id=input_data.project_id)
            creator_as_mentor = Mentor.objects.get(nest_user=user)
        except (Program.DoesNotExist, Project.DoesNotExist) as e:
            # Grouping not-found errors into a single specific exception type.
            msg = f"{e.__class__.__name__} matching query does not exist."
            raise ObjectDoesNotExist(msg) from e
        except Mentor.DoesNotExist as e:
            # PermissionDenied is the correct Django exception for role/status checks.
            msg = "Only mentors can create modules."
            raise PermissionDenied(msg) from e

        if creator_as_mentor not in program.admins.all():
            msg = "You must be an admin of this program to create a module."
            raise PermissionDenied(msg)

        if (
            input_data.ended_at
            and input_data.started_at
            and input_data.ended_at <= input_data.started_at
        ):
            # ValidationError is the standard Django exception for invalid data.
            msg = "End date must be after start date."
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

        mentors_to_set = _resolve_mentors_from_logins(input_data.mentor_logins or [])
        mentors_to_set.add(creator_as_mentor)
        module.mentors.set(list(mentors_to_set))

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_module(self, info: strawberry.Info, input_data: UpdateModuleInput) -> ModuleNode:
        """Update an existing mentorship module. User must be an admin of the program."""
        username = info.context.request.user
        user_entities = get_user_entities_by_github_username(username)

        if not user_entities:
            msg = "Logic error: Authenticated user not found in the database."
            raise ObjectDoesNotExist(msg)

        github_user, user = user_entities

        try:
            module = Module.objects.select_related("program").get(key=input_data.key)
            creator_as_mentor = Mentor.objects.get(nest_user=user)
        except Module.DoesNotExist as e:
            msg = "Module not found."
            raise ObjectDoesNotExist(msg) from e
        except Mentor.DoesNotExist as e:
            msg = "Only mentors can edit modules."
            raise PermissionDenied(msg) from e

        if creator_as_mentor not in module.program.admins.all():
            msg = "You must be an admin of the module's program to edit it."
            raise PermissionDenied(msg)

        module.name = input_data.name
        module.key = slugify(input_data.name)

        if input_data.description is not None:
            module.description = input_data.description
        if input_data.experience_level is not None:
            module.experience_level = input_data.experience_level.value
        if input_data.started_at is not None:
            module.started_at = input_data.started_at
        if input_data.ended_at is not None:
            module.ended_at = input_data.ended_at
        if input_data.domains is not None:
            module.domains = input_data.domains
        if input_data.tags is not None:
            module.tags = input_data.tags

        if module.ended_at and module.started_at and module.ended_at <= module.started_at:
            msg = "End date must be after start date."
            raise ValidationError(msg)

        if input_data.project_id is not None:
            try:
                module.project = Project.objects.get(id=input_data.project_id)
            except Project.DoesNotExist as e:
                msg = f"Project with id '{input_data.project_id}' not found."
                raise ObjectDoesNotExist(msg) from e

        if input_data.mentor_logins is not None:
            mentors_to_set = _resolve_mentors_from_logins(input_data.mentor_logins)
            module.mentors.set(list(mentors_to_set))

        module.save()

        return module
