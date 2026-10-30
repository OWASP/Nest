"""Database-backed membership regressions for My Mentorship."""

from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone

from apps.github.models import User as GithubUser
from apps.mentorship.api.internal.mutations.program import resolve_admins_from_logins
from apps.mentorship.api.internal.queries.program import ProgramQuery
from apps.mentorship.models import Admin, Mentee, Mentor, Module, Program
from apps.mentorship.models.mentee_module import MenteeModule
from apps.mentorship.models.mentor_module import MentorModule
from apps.mentorship.models.program_admin import ProgramAdmin
from apps.owasp.models.project import Project
from settings.graphql import schema


def _create_github_user(login: str) -> GithubUser:
    """Persist a GitHub identity without triggering external indexing signals."""
    now = timezone.now()
    return GithubUser.objects.bulk_create(
        [GithubUser(login=login, node_id=login, created_at=now, updated_at=now)]
    )[0]


def _create_program(key: str, name: str = "") -> Program:
    """Persist a program without triggering external indexing signals."""
    now = timezone.now()
    return Program.objects.bulk_create(
        [Program(key=key, name=name or key, started_at=now, ended_at=now + timedelta(days=90))]
    )[0]


def _request_info(user) -> SimpleNamespace:
    """Build resolver context with an actual authenticated Nest user."""
    return SimpleNamespace(context=SimpleNamespace(request=SimpleNamespace(user=user)))


def _create_nest_user(user_model, username: str, github_user: GithubUser | None = None):
    """Persist a Nest account with password authentication disabled."""
    user = user_model(username=username, github_user=github_user)
    user.set_unusable_password()
    return user_model.objects.bulk_create([user])[0]


def _add_module_roles(program: Program, github_user: GithubUser, role: str) -> None:
    """Persist module roles, including duplicate joins for the same program."""
    now = timezone.now()
    project = Project.objects.bulk_create(
        [
            Project(
                key="membership-project", name="Membership project", created_at=now, updated_at=now
            )
        ]
    )[0]
    modules = Module.objects.bulk_create(
        [
            Module(
                key=f"membership-module-{index}",
                program=program,
                project=project,
                started_at=now,
                ended_at=now + timedelta(days=90),
            )
            for index in range(2)
        ]
    )
    if role in {"mentor", "both"}:
        mentor = Mentor.objects.bulk_create([Mentor(github_user=github_user)])[0]
        MentorModule.objects.bulk_create(
            [MentorModule(mentor=mentor, module=module) for module in modules]
        )
    if role in {"mentee", "both"}:
        mentee = Mentee.objects.bulk_create([Mentee(github_user=github_user)])[0]
        MenteeModule.objects.bulk_create(
            [MenteeModule(mentee=mentee, module=module, started_at=now) for module in modules]
        )


@pytest.fixture
def invited_admin(django_user_model) -> SimpleNamespace:
    """Invite and assign the GitHub admin before their Nest account exists."""
    github_user = _create_github_user("invited-admin")
    admin = resolve_admins_from_logins([github_user.login]).pop()
    assert admin.nest_user_id is None
    program = _create_program("invited-program")
    ProgramAdmin.objects.create(admin=admin, program=program)
    user = _create_nest_user(django_user_model, "invited-admin", github_user)
    return SimpleNamespace(admin=admin, github_user=github_user, program=program, user=user)


@pytest.mark.django_db
class TestMyProgramsMembership:
    """Exercise actual PostgreSQL membership selection and role classification."""

    @pytest.mark.parametrize("linked", [False, True])
    @pytest.mark.parametrize("other_role", ["none", "mentor", "mentee", "both"])
    def test_admin_membership_and_role_precedence(self, invited_admin, linked, other_role):
        """Linked and GitHub-only admins retain their highest role across joins."""
        if linked:
            Admin.objects.filter(pk=invited_admin.admin.pk).update(nest_user=invited_admin.user)
        if other_role != "none":
            _add_module_roles(invited_admin.program, invited_admin.github_user, other_role)

        result = ProgramQuery().my_programs(_request_info(invited_admin.user))

        assert [(program.pk, program.user_role) for program in result.programs] == [
            (invited_admin.program.pk, "admin")
        ]
        invited_admin.admin.refresh_from_db()
        assert invited_admin.admin.nest_user_id == (invited_admin.user.pk if linked else None)

    def test_unrelated_user_has_no_membership(self, invited_admin, django_user_model):
        """An unrelated GitHub identity cannot discover another admin's program."""
        github_user = _create_github_user("unrelated-user")
        user = _create_nest_user(django_user_model, "unrelated-user", github_user)

        result = ProgramQuery().my_programs(_request_info(user))

        assert result.programs == []
        assert result.current_page == result.total_pages == 1

    def test_admin_without_github_account(self, invited_admin, django_user_model):
        """Nest-only admins see their own program without matching null links."""
        user = _create_nest_user(django_user_model, "nest-only-admin")
        github_user = _create_github_user("nest-only-admin")
        admin = Admin.objects.create(github_user=github_user, nest_user=user)
        program = _create_program("nest-only-program")
        ProgramAdmin.objects.create(admin=admin, program=program)

        result = ProgramQuery().my_programs(_request_info(user))

        assert [(item.pk, item.user_role) for item in result.programs] == [(program.pk, "admin")]

    def test_search_pagination_and_duplicate_memberships(self, invited_admin):
        """Search and pagination retain only owned programs and deduplicate joins."""
        first = invited_admin.program
        second = _create_program("second-program", "Needle beta")
        other = _create_program("other-program", "Other program")
        _create_program("unrelated-program", "Needle unrelated")
        ProgramAdmin.objects.bulk_create(
            [
                ProgramAdmin(admin=invited_admin.admin, program=program)
                for program in (second, other)
            ]
        )
        now = timezone.now()
        Program.objects.filter(pk=first.pk).update(name="Needle alpha", nest_created_at=now)
        Program.objects.filter(pk=second.pk).update(nest_created_at=now + timedelta(seconds=1))
        _add_module_roles(first, invited_admin.github_user, "both")
        query = ProgramQuery()
        info = _request_info(invited_admin.user)

        first_page = query.my_programs(info, search="NEEDLE", limit=1)
        second_page = query.my_programs(info, search="needle", page=2, limit=1)

        assert first_page.total_pages == second_page.total_pages == 2
        assert [(program.pk, program.user_role) for program in first_page.programs] == [
            (second.pk, "admin")
        ]
        assert [(program.pk, program.user_role) for program in second_page.programs] == [
            (first.pk, "admin")
        ]
        assert query.my_programs(info, search="needle", page=99, limit=1).current_page == 2
        assert query.my_programs(info, search="needle", page=0, limit=1).current_page == 1

    def test_first_sign_in_graphql_membership(self, invited_admin):
        """The actual authenticated GraphQL query returns the invited admin's program."""
        response = schema.execute_sync(
            "{ myPrograms { currentPage totalPages programs { key userRole } } }",
            context_value=_request_info(invited_admin.user).context,
        )

        assert response.errors is None
        assert response.data is not None
        assert response.data["myPrograms"] == {
            "currentPage": 1,
            "totalPages": 1,
            "programs": [{"key": invited_admin.program.key, "userRole": "admin"}],
        }
