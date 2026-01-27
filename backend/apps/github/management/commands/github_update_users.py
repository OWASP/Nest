"""A command to update GitHub users."""

import logging

from django.core.management.base import BaseCommand
from django.db.models import Q, Sum

from apps.common.models import BATCH_SIZE
from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User
from apps.owasp.models.member_profile import MemberProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update GitHub users."

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        active_users = User.objects.order_by("-created_at")
        active_users_count = active_users.count()
        offset = options["offset"]
        user_contributions = {
            item["user_id"]: item["total_contributions"]
            for item in RepositoryContributor.objects.exclude(
                Q(repository__is_fork=True)
                | Q(repository__organization__is_owasp_related_organization=False)
                | Q(user__login__in=User.get_non_indexable_logins()),
            )
            .values("user_id")
            .annotate(total_contributions=Sum("contributions_count"))
        }
        users = []
        profiles = []
        for idx, user in enumerate(active_users[offset:]):
            prefix = f"{idx + offset + 1} of {active_users_count - offset}"
            print(f"{prefix:<10} {user.title}")

            profile, created = MemberProfile.objects.get_or_create(github_user=user)

            if created:
                profile.github_user = user

            contributions = user_contributions.get(user.id, 0)

            profile.contributions_count = contributions
            profiles.append(profile)

            user.contributions_count = contributions
            users.append(user)

            if not len(users) % BATCH_SIZE:
                User.bulk_save(users, fields=("contributions_count",))
                MemberProfile.bulk_save(
                    profiles,
                    fields=("contributions_count",),
                )

        User.bulk_save(users, fields=("contributions_count",))
        MemberProfile.bulk_save(
            profiles,
            fields=("contributions_count",),
        )
