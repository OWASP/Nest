"""Mentorship Program GraphQL Mutations."""

import logging

import strawberry
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
from apps.common.utils import slugify
from apps.github.models import User as GithubUser
from apps.mentorship.graphql.nodes.program import (
    CreateProgramInput,
    ProgramNode,
    UpdateProgramInput,
)
from apps.mentorship.models import Mentor, Program
from apps.mentorship.utils.user import get_authenticated_user

logger = logging.getLogger(__name__)


@strawberry.type
class ProgramMutation:
    """GraphQL mutations related to program."""

    @strawberry.mutation
    @transaction.atomic
    def create_program(
        self, info: strawberry.Info, input_data: CreateProgramInput
    ) -> ProgramNode:
        """
        Create a new mentorship program.
        """
        request = info.context.request
        user = get_authenticated_user(request)
        mentor, created = Mentor.objects.get_or_create(
            nest_user=user, defaults={"github_user": user.github_user}
        )
        if created:
            logger.info("Created a new mentor profile for user '%s'.", user.email)

        if input_data.ended_at <= input_data.started_at:
            msg = "End date must be after start date."
            logger.warning(
                "Validation error for user '%s' creating program '%s': %s",
                user.email,
                input_data.name,
                msg,
            )
            raise strawberry.GraphQLError(msg)

        program = Program.objects.create(
            name=input_data.name,
            key=slugify(input_data.name),
            description=input_data.description,
            experience_levels=[lvl.value for lvl in input_data.experience_levels],
            mentees_limit=input_data.mentees_limit,
            started_at=input_data.started_at,
            ended_at=input_data.ended_at,
            domains=input_data.domains,
            tags=input_data.tags,
            status=input_data.status.value,
        )

        program.admins.set([mentor])

        logger.info(
            "User '%s' successfully created program '%s' (ID: %s).",
            user.email,
            program.name,
            program.id,
        )

        return program

    @strawberry.mutation
    def update_program(
        self, info: strawberry.Info, input_data: UpdateProgramInput
    ) -> ProgramNode:
        """Update an existing mentorship program. Only admins can update."""
        request = info.context.request
        user = get_authenticated_user(request)

        try:
            program = Program.objects.get(key=input_data.key)
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
                user.email,
                exc_info=True,
            )
            raise PermissionDenied(msg) from err

        if admin not in program.admins.all():
            msg = "You must be an admin of this program to update it."
            logger.warning(
                "Permission denied for user '%s' to update program '%s'.",
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
            logger.warning(
                "Validation error updating program '%s': %s", program.key, msg
            )
            raise ValidationError(msg)

        simple_fields = {
            "key": slugify(input_data.name),
            "name": input_data.name,
            "description": input_data.description,
            "mentees_limit": input_data.mentees_limit,
            "started_at": input_data.started_at,
            "ended_at": input_data.ended_at,
            "domains": input_data.domains,
            "tags": input_data.tags,
        }

        for field, value in simple_fields.items():
            if value is not None:
                setattr(program, field, value)

        if input_data.experience_levels is not None:
            program.experience_levels = [
                lvl.value for lvl in input_data.experience_levels
            ]

        if input_data.status is not None:
            program.status = input_data.status.value

        program.save()

        if input_data.admin_logins is not None:
            resolved_mentors = []
            for login in input_data.admin_logins:
                try:
                    github_user = GithubUser.objects.get(login__iexact=login.lower())
                    mentor, _ = Mentor.objects.get_or_create(github_user=github_user)
                    resolved_mentors.append(mentor)
                except GithubUser.DoesNotExist as err:
                    msg = f"GitHub user '{login}' not found."
                    logger.warning(msg, exc_info=True)
                    raise ObjectDoesNotExist(msg) from err

            program.admins.set(resolved_mentors)

        return program
