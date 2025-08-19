"""GraphQL mutations for mentorship modules in the mentorship app."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.module import (
    CreateModuleInput,
    ModuleNode,
    UpdateModuleInput,
)
from apps.mentorship.models import Mentor, Module, Program
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.owasp.models import Project

logger = logging.getLogger(__name__)


def resolve_mentors_from_logins(logins: list[str]) -> set[Mentor]:
    """Resolve a list of GitHub logins to a set of Mentor objects."""
    mentors = set()
    for login in logins:
        try:
            github_user = GithubUser.objects.get(login__iexact=login.lower())
            mentor, _ = Mentor.objects.get_or_create(github_user=github_user)
            mentors.add(mentor)
        except GithubUser.DoesNotExist as e:
            msg = f"GitHub user '{login}' not found."
            logger.warning(msg, exc_info=True)
            raise ValueError(msg) from e
    return mentors


def _validate_module_dates(started_at, ended_at, program_started_at, program_ended_at) -> tuple:
    """Validate and normalize module start/end dates against program constraints."""
    if started_at is None or ended_at is None:
        msg = "Both start and end dates are required."
        raise ValidationError(message=msg)

    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at)
    if timezone.is_naive(ended_at):
        ended_at = timezone.make_aware(ended_at)

    if ended_at <= started_at:
        msg = "End date must be after start date."
        raise ValidationError(message=msg)

    if started_at < program_started_at:
        msg = "Module start date cannot be before program start date."
        raise ValidationError(message=msg)

    if ended_at > program_ended_at:
        msg = "Module end date cannot be after program end date."
        raise ValidationError(message=msg)

    return started_at, ended_at


@strawberry.type
class ModuleMutation:
    """GraphQL mutations related to the mentorship Module model."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_module(self, info: strawberry.Info, input_data: CreateModuleInput) -> ModuleNode:
        """Create a new mentorship module. User must be an admin of the program."""
        user = info.context.request.user

        try:
            program = Program.objects.get(key=input_data.program_key)
            project = Project.objects.get(id=input_data.project_id)
            creator_as_mentor = Mentor.objects.get(nest_user=user)
        except (Program.DoesNotExist, Project.DoesNotExist) as e:
            msg = f"{e.__class__.__name__} matching query does not exist."
            raise ObjectDoesNotExist(msg) from e
        except Mentor.DoesNotExist as e:
            msg = "Only mentors can create modules."
            raise PermissionDenied(msg) from e

        if not program.admins.filter(id=creator_as_mentor.id).exists():
            raise PermissionDenied

        started_at, ended_at = _validate_module_dates(
            input_data.started_at,
            input_data.ended_at,
            program.started_at,
            program.ended_at,
        )

        module = Module.objects.create(
            name=input_data.name,
            description=input_data.description,
            experience_level=input_data.experience_level.value,
            started_at=started_at,
            ended_at=ended_at,
            domains=input_data.domains,
            tags=input_data.tags,
            program=program,
            project=project,
        )

        if module.experience_level not in program.experience_levels:
            program.experience_levels.append(module.experience_level)
            program.save(update_fields=["experience_levels"])

        mentors_to_set = resolve_mentors_from_logins(input_data.mentor_logins or [])
        mentors_to_set.add(creator_as_mentor)
        module.mentors.set(list(mentors_to_set))

        return module

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_module(self, info: strawberry.Info, input_data: UpdateModuleInput) -> ModuleNode:
        """Update an existing mentorship module. User must be an admin of the program."""
        user = info.context.request.user

        try:
            module = Module.objects.select_related("program").get(
                key=input_data.key, program__key=input_data.program_key
            )
        except Module.DoesNotExist as e:
            msg = "Module not found."
            raise ObjectDoesNotExist(msg) from e

        try:
            creator_as_mentor = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            msg = "Only mentors can edit modules."
            logger.warning(
                "User '%s' is not a mentor and cannot edit modules.",
                user.username,
                exc_info=True,
            )
            raise PermissionDenied(msg) from err

        if not module.program.admins.filter(id=creator_as_mentor.id).exists():
            raise PermissionDenied

        started_at, ended_at = _validate_module_dates(
            input_data.started_at,
            input_data.ended_at,
            module.program.started_at,
            module.program.ended_at,
        )

        old_experience_level = module.experience_level

        field_mapping = {
            "name": input_data.name,
            "description": input_data.description,
            "experience_level": input_data.experience_level.value,
            "started_at": started_at,
            "ended_at": ended_at,
            "domains": input_data.domains,
            "tags": input_data.tags,
        }

        for field, value in field_mapping.items():
            setattr(module, field, value)

        try:
            module.project = Project.objects.get(id=input_data.project_id)
        except Project.DoesNotExist as err:
            msg = f"Project with id '{input_data.project_id}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

        if input_data.mentor_logins is not None:
            mentors_to_set = resolve_mentors_from_logins(input_data.mentor_logins)
            module.mentors.set(mentors_to_set)

        module.save()

        if module.experience_level not in module.program.experience_levels:
            module.program.experience_levels.append(module.experience_level)

        # Remove old experience level if no other module is using it
        if (
            old_experience_level != module.experience_level
            and old_experience_level in module.program.experience_levels
            and not Module.objects.filter(
                program=module.program, experience_level=old_experience_level
            )
            .exclude(id=module.id)
            .exists()
        ):
            module.program.experience_levels.remove(old_experience_level)

        module.program.save(update_fields=["experience_levels"])

        return module
