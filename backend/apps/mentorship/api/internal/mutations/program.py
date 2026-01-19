"""Mentorship Program GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction

from apps.common.extensions import invalidate_program_cache
from apps.mentorship.api.internal.mutations.module import resolve_mentors_from_logins
from apps.mentorship.api.internal.nodes.enum import ProgramStatusEnum
from apps.mentorship.api.internal.nodes.program import (
    CreateProgramInput,
    ProgramNode,
    UpdateProgramInput,
    UpdateProgramStatusInput,
)
from apps.mentorship.models import Mentor, Program
from apps.nest.api.internal.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@strawberry.type
class ProgramMutation:
    """GraphQL mutations related to program."""

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    @transaction.atomic
    def create_program(self, info: strawberry.Info, input_data: CreateProgramInput) -> ProgramNode:
        """Create a new mentorship program."""
        user = info.context.request.user

        mentor, created = Mentor.objects.get_or_create(
            nest_user=user, defaults={"github_user": user.github_user}
        )
        if created:
            logger.info("Created a new mentor profile for user '%s'.", user.username)

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

        program.admins.set([mentor])

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

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            msg = "You must be a mentor to update a program."
            logger.warning(
                "User '%s' is not a mentor and cannot update programs.",
                user.username,
                exc_info=True,
            )
            raise PermissionDenied(msg) from err

        if not program.admins.filter(id=admin.id).exists():
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
            admins_to_set = resolve_mentors_from_logins(input_data.admin_logins)
            program.admins.set(admins_to_set)

        invalidate_program_cache(old_key)
        if program.key != old_key:
            invalidate_program_cache(program.key)

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

        try:
            mentor = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as e:
            msg = "You must be a mentor to update a program."
            raise PermissionDenied(msg) from e

        if not program.admins.filter(id=mentor.id).exists():
            raise PermissionDenied

        program.status = input_data.status.value
        program.save()

        invalidate_program_cache(program.key)

        logger.info("Updated status of program '%s' to '%s'", program.key, program.status)

        return program
