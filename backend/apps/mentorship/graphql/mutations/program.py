import strawberry
from github import Github

from apps.github.models import User as GithubUser
from apps.mentorship.graphql.nodes.program import (
    CreateProgramInput,
    ProgramNode,
    UpdateProgramInput,
)
from apps.mentorship.models import Mentor, Program
from apps.nest.models import User as NestUser


def get_authenticated_user(request) -> NestUser:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid Authorization header")

    access_token = auth_header.removeprefix("Bearer ").strip()
    try:
        github = Github(access_token)
        gh_user = github.get_user()
        login = gh_user.login
        name = gh_user.name
    except Exception:
        raise Exception("GitHub token is invalid or expired")

    try:
        github_user = GithubUser.objects.get(login=login)
    except GithubUser.DoesNotExist:
        raise Exception("No GithubUser found for this login")

    try:
        user = NestUser.objects.get(github_user=github_user)
    except NestUser.DoesNotExist:
        raise Exception("No linked Nest user found for this GitHub account")

    return user


@strawberry.type
class ProgramMutation:
    """GraphQL mutations related to program."""

    @strawberry.mutation
    def create_program(
        self, info: strawberry.Info, input: CreateProgramInput
    ) -> ProgramNode:
        request = info.context.request
        user = get_authenticated_user(request)

        if user.role != "mentor":
            raise Exception("you must be a mentor to create a program")

        if input.ended_at <= input.started_at:
            raise Exception("End date must be after start date")

        mentor, _ = Mentor.objects.get_or_create(
            nest_user=user, defaults={"github_user": user.github_user}
        )

        program = Program.objects.create(
            name=input.name,
            description=input.description,
            experience_levels=[lvl.value for lvl in input.experience_levels],
            mentees_limit=input.mentees_limit,
            started_at=input.started_at,
            ended_at=input.ended_at,
            domains=input.domains,
            tags=input.tags,
            status=input.status.value,
        )

        program.admins.add(mentor)

        return program

    @strawberry.mutation
    def update_program(
        self, info: strawberry.Info, input: UpdateProgramInput
    ) -> ProgramNode:
        request = info.context.request
        user = get_authenticated_user(request)

        try:
            program = Program.objects.get(id=input.id)
        except Program.DoesNotExist:
            raise Exception("Program not found")

        try:
            mentor = Mentor.objects.get(nest_user=user)
        except Mentor.DoesNotExist:
            raise Exception("You must be a mentor to update a program")

        if mentor not in program.admins.all():
            raise Exception("You must be an admin of this program to update it")

        for field, value in input.__dict__.items():
            if field in ["admin_logins", "id"]:
                continue
            setattr(program, field, value)

        program.save()

        resolved_mentors = []

        for login in input.admin_logins:
            try:
                github_user = GithubUser.objects.get(login=login)
            except GithubUser.DoesNotExist:
                raise Exception(f"GitHub user with login '{login}' not found.")

            mentor, created = Mentor.objects.get_or_create(github_user=github_user)
            resolved_mentors.append(mentor)

        program.admins.set(resolved_mentors)

        return ProgramNode(
            id=program.id,
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
