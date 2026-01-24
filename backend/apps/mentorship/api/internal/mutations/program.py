"""Mentorship Program GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction

from apps.api.internal.extensions.cache import invalidate_program_cache
from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.nodes.enum import ProgramStatusEnum
from apps.mentorship.api.internal.nodes.program import (
    CreateProgramInput,
    ProgramNode,
    UpdateProgramInput,
    UpdateProgramStatusInput,
)
from apps.mentorship.models import Admin, Program
from apps.mentorship.models.program_admin import ProgramAdmin
from apps.nest.api.internal.permissions import IsAuthenticated
from apps.nest.models import User

logger = logging.getLogger(__name__)


def resolve_admins_from_logins(logins: list[str]) -> set:
    """Resolve a list of GitHub logins to a set of Admin objects."""
    admins = set()
    for login in logins:
        try:
            github_user = GithubUser.objects.get(login__iexact=login.lower())
            admin, _ = Admin.objects.get_or_create(github_user=github_user)
            if not admin.nest_user:
                try:
                    nest_user = User.objects.get(github_user=github_user)
                    admin.nest_user = nest_user
                    admin.save(update_fields=["nest_user"])
                except User.DoesNotExist:
                    pass
            admins.add(admin)
        except GithubUser.DoesNotExist as e:
            msg = f"GitHub user '{login}' not found."
            logger.warning(msg, exc_info=True)
            raise ValueError(msg) from e
    return admins


@strawberry.type
class ProgramMutation:
    """GraphQL mutations related to program."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_program(self, info: strawberry.Info, input_data: CreateProgramInput) -> ProgramNode:
        """Create a new mentorship program."""
        user = info.context.request.user

        if input_data.ended_at <= input_data.started_at:
            msg = "End date must be after start date."
            logger.warning(
                "Validation error for user '%s' creating program '%s': %s",
                user.username,
                input_data.name,
                msg,
            )
            raise ValidationError(msg)

        program = Program.objects.create(
            name=input_data.name,
            description=input_data.description,
            mentees_limit=input_data.mentees_limit,
            started_at=input_data.started_at,
            ended_at=input_data.ended_at,
            domains=input_data.domains,
            tags=input_data.tags,
            status=ProgramStatusEnum.DRAFT.value,
        )

        admin, _ = Admin.objects.get_or_create(github_user=user.github_user)
        if not admin.nest_user:
            admin.nest_user = user
            admin.save(update_fields=["nest_user"])
        ProgramAdmin.objects.create(
            program=program, admin=admin, role=ProgramAdmin.AdminRole.OWNER
        )

        logger.info(
            "User '%s' successfully created program '%s' (ID: %s).",
            user.username,
            program.name,
            program.id,
        )

        return program

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_program(self, info: strawberry.Info, input_data: UpdateProgramInput) -> ProgramNode:
        """Update an existing mentorship program. Only admins can update."""
        user = info.context.request.user

        try:
            program = Program.objects.get(key=input_data.key)
            old_key = program.key
        except Program.DoesNotExist as err:
            msg = f"Program with key '{input_data.key}' not found."
            logger.warning(msg, exc_info=True)
            raise ObjectDoesNotExist(msg) from err

        if not program.admins.filter(nest_user=user).exists():
            msg = "You must be an admin of this program to update it."
            logger.warning(
                "Permission denied for user '%s' to update program '%s'.",
                user.username,
                program.key,
            )
            raise PermissionDenied(msg)

        if (
            input_data.ended_at is not None
            and input_data.started_at is not None
            and input_data.ended_at <= input_data.started_at
        ):
            msg = "End date must be after start date."
            logger.warning("Validation error updating program '%s': %s", program.key, msg)
            raise ValidationError(msg)

        field_mapping = {
            "name": input_data.name,
            "description": input_data.description,
            "mentees_limit": input_data.mentees_limit,
            "started_at": input_data.started_at,
            "ended_at": input_data.ended_at,
            "domains": input_data.domains,
            "tags": input_data.tags,
        }

        for field, value in field_mapping.items():
            if value is not None:
                setattr(program, field, value)

        if input_data.status is not None:
            program.status = input_data.status.value

        program.save()

        if input_data.admin_logins is not None:
            admins_to_set = resolve_admins_from_logins(input_data.admin_logins)
            program.admins.set(admins_to_set)

        def _invalidate():
            invalidate_program_cache(old_key)
            if program.key != old_key:
                invalidate_program_cache(program.key)

        transaction.on_commit(_invalidate)

        return program

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def update_program_status(
        self, info: strawberry.Info, input_data: UpdateProgramStatusInput
    ) -> ProgramNode:
        """Update only the status of a program."""
        user = info.context.request.user

        try:
            program = Program.objects.get(key=input_data.key)
        except Program.DoesNotExist as e:
            msg = f"Program with key '{input_data.key}' not found."
            raise ObjectDoesNotExist(msg) from e

        if not program.admins.filter(nest_user=user).exists():
            raise PermissionDenied

        program.status = input_data.status.value
        program.save()

        transaction.on_commit(lambda: invalidate_program_cache(program.key))

        logger.info("Updated status of program '%s' to '%s'", program.key, program.status)

        return program
