"""A command to update GitHub users."""

import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Q, Sum

from apps.common.models import BATCH_SIZE
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
        for idx, user in enumerate(active_users[offset:]):
            prefix = f"{idx + offset + 1} of {active_users_count - offset}"
            print(f"{prefix:<10} {user.title}")

            user.contributions_count = user_contributions.get(user.id, 0)
            users.append(user)

            if not len(users) % BATCH_SIZE:
                User.bulk_save(users, fields=("contributions_count",))

        User.bulk_save(users, fields=("contributions_count",))

        # Sync badges after user data refresh
        self.stdout.write("Syncing badges...")

        badge_sync_failed = False

        try:
            call_command("nest_update_staff_badges", stdout=self.stdout)
        except Exception as e:
            logger.exception("Staff badge sync failed")
            self.stderr.write(self.style.ERROR(f"Staff badge sync failed: {e}"))
            badge_sync_failed = True
        try:
            call_command("nest_update_project_leader_badges", stdout=self.stdout)
        except Exception as e:
            logger.exception("Project leader badge sync failed")
            self.stderr.write(self.style.ERROR(f"Project leader badge sync failed: {e}"))
            badge_sync_failed = True

        if badge_sync_failed:
            self.stderr.write(
                self.style.WARNING("User update completed but badge sync had errors")
            )
