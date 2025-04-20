"""A command to update GitHub users."""

import logging

from django.core.management.base import BaseCommand
from django.db.models import Sum

from apps.github.models.repository_contributor import RepositoryContributor
from apps.github.models.user import User

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
        offset = options["offset"]
        active_users = User.objects.order_by("-created_at")
        active_users_count = active_users.count()
        users = []
        for idx, user in enumerate(active_users[offset:]):
            prefix = f"{idx + offset + 1} of {active_users_count - offset}"
            print(f"{prefix:<10} {user.title}")

            user.contributions_count = (
                RepositoryContributor.objects.filter(
                    user=user,
                ).aggregate(
                    total_contributions=Sum(
                        "contributions_count",
                    )
                )["total_contributions"]
                or 0
            )
            users.append(user)

            if not len(users) % 1000:
                User.bulk_save(users, fields=("contributions_count",))

        User.bulk_save(users, fields=("contributions_count",))
