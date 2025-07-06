"""Mentorship Program GraphQL Mutations."""

import strawberry

from apps.common.utils import slugify
from apps.github.models import User as GithubUser
from apps.mentorship.graphql.nodes.program import (
    CreateProgramInput,
    ProgramNode,
    UpdateProgramInput,
)
from apps.mentorship.models import Mentor, Program
from apps.mentorship.utils.user import get_authenticated_user


@strawberry.type
class ProgramMutation:
    """GraphQL mutations related to program."""

    @strawberry.mutation
    def create_program(self, info: strawberry.Info, input_data: CreateProgramInput) -> ProgramNode:
        """Create a new mentorship program if the user is a mentor."""
        request = info.context.request
        user = get_authenticated_user(request)

        if user.role != "mentor":
            raise Exception("You must be a mentor to create a program")

        if input_data.ended_at <= input_data.started_at:
            raise Exception("End date must be after start date")

        mentor, _ = Mentor.objects.get_or_create(
            nest_user=user, defaults={"github_user": user.github_user}
        )

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

        resolved_mentors = {mentor}

        for login in input_data.admin_logins:
            try:
                github_user = GithubUser.objects.get(login__iexact=login.lower())
            except GithubUser.DoesNotExist as err:
                raise Exception("GitHub user with username not found.") from err
            m, _ = Mentor.objects.get_or_create(github_user=github_user)
            resolved_mentors.add(m)

        program.admins.set(resolved_mentors)

        return ProgramNode(
            id=program.id,
            key=program.key,
            name=program.name,
            description=program.description,
            experience_levels=program.experience_levels,
            mentees_limit=program.mentees_limit,
            started_at=program.started_at,
            ended_at=program.ended_at,
            domains=program.domains,
            tags=program.tags,
            status=program.status,
            admins=list(program.admins.all()),
        )

    @strawberry.mutation
    def update_program(self, info: strawberry.Info, input_data: UpdateProgramInput) -> ProgramNode:
        """Update an existing mentorship program. Only admins can update."""
        request = info.context.request
        user = get_authenticated_user(request)

        try:
            program = Program.objects.get(key=input_data.key)
        except Program.DoesNotExist as err:
            raise Exception("Program not found") from err

        try:
            admin = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist as err:
            raise Exception("You must be a mentor to update a program") from err

        if admin not in program.admins.all():
            raise Exception("You must be an admin of this program to update it")

        if (
            input_data.ended_at is not None
            and input_data.started_at is not None
            and input_data.ended_at <= input_data.started_at
        ):
            raise Exception("End date must be after start date")

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
            program.experience_levels = [lvl.value for lvl in input_data.experience_levels]

        if input_data.status is not None:
            program.status = input_data.status.value

        program.save()

        if input_data.admin_logins is not None:
            resolved_mentors = []
            for login in input_data.admin_logins:
                try:
                    github_user = GithubUser.objects.get(login__iexact=login.lower())
                except GithubUser.DoesNotExist as err:
                    raise Exception("GitHub user not found.") from err

                mentor, _ = Mentor.objects.get_or_create(github_user=github_user)
                resolved_mentors.append(mentor)

            program.admins.set(resolved_mentors)

        return ProgramNode(
            id=program.id,
            key=program.key,
            name=program.name,
            description=program.description,
            experience_levels=program.experience_levels,
            mentees_limit=program.mentees_limit,
            started_at=program.started_at,
            ended_at=program.ended_at,
            domains=program.domains,
            tags=program.tags,
            status=program.status,
            admins=list(program.admins.all()),
        )
