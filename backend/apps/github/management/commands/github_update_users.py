"""A command to update GitHub users."""

import logging

from django.core.management.base import BaseCommand

from apps.common.models import BATCH_SIZE
from apps.github.models.user import User
from apps.github.services.score import compute_user_score, get_scoring_context

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

        context = get_scoring_context()

        users = []
        for idx, user in enumerate(active_users[offset:].iterator()):
            prefix = f"{idx + 1} of {active_users_count - offset}"
            self.stdout.write(f"{prefix:<10} {user.title}\n")

            repo_item = context["repo_data_map"].get(user.id, {})
            user.contributions_count = repo_item.get("total_contributions", 0)
            user.calculated_score = compute_user_score(user, context)

            users.append(user)

            if not len(users) % BATCH_SIZE:
                User.bulk_save(list(users), fields=("contributions_count", "calculated_score"))
                users.clear()

        if users:
            User.bulk_save(list(users), fields=("contributions_count", "calculated_score"))
