"""Seed deterministic users for end-to-end tests."""

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.core.utils import index
from apps.github.models.user import User as GithubUser
from apps.mentorship.models import Mentee, Mentor
from apps.nest.models import User as NestUser
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project

E2E_USERS = (
    ("e2e-mentee", "mentee"),
    ("e2e-mentor", "mentor"),
    ("e2e-user", ""),
)


class Command(BaseCommand):
    help = "Seed e2e test users."

    def handle(self, *_args, **_options) -> None:
        """Create GitHub, Nest, and mentorship users for e2e tests."""
        if not settings.IS_E2E_ENVIRONMENT:
            error_message = "This command can only run in the e2e environment."
            raise CommandError(error_message)

        now = timezone.now()
        with index.disable_indexing():
            for login, role in E2E_USERS:
                github_user, _ = GithubUser.objects.get_or_create(
                    login=login,
                    defaults={
                        "created_at": now,
                        "email": f"{login}@example.com",
                        "name": login,
                        "node_id": f"e2e_node_{login}",
                        "updated_at": now,
                    },
                )
                nest_user, _ = NestUser.objects.get_or_create(
                    username=login,
                    defaults={
                        "email": f"{login}@example.com",
                        "github_user": github_user,
                    },
                )
                if nest_user.github_user_id != github_user.id:
                    nest_user.github_user = github_user
                    nest_user.save(update_fields=["github_user"])
                if role == "mentor":
                    Mentor.objects.get_or_create(
                        github_user=github_user,
                        defaults={"nest_user": nest_user},
                    )
                elif role == "mentee":
                    Mentee.objects.get_or_create(
                        github_user=github_user,
                        defaults={"nest_user": nest_user},
                    )
                elif login == "e2e-user":
                    project, _ = Project.objects.get_or_create(
                        key="www-project-e2e",
                        defaults={"name": "E2E Project"},
                    )
                    membership, _ = EntityMember.objects.get_or_create(
                        entity_id=project.id,
                        entity_type=ContentType.objects.get_for_model(Project),
                        member_name=login,
                        role=EntityMember.Role.LEADER,
                        defaults={
                            "is_active": True,
                            "is_reviewed": True,
                            "member": github_user,
                        },
                    )
                    membership.is_active = True
                    membership.is_reviewed = True
                    membership.member = github_user
                    membership.save(update_fields=["is_active", "is_reviewed", "member"])
