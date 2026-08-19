"""Seed deterministic users for end-to-end tests."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.core.utils import index
from apps.github.models.user import User as GithubUser
from apps.mentorship.models import Mentee, Mentor
from apps.nest.models import User as NestUser

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
