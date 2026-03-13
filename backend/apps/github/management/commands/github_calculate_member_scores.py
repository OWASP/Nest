"""A command to calculate member ranking scores."""

import logging
from typing import Any

from django.core.management.base import BaseCommand

from apps.common.models import BATCH_SIZE
from apps.github.models.user import User
from apps.github.services.score import MemberScoreCalculator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Calculate composite ranking scores for OWASP community members."""

    help = "Calculate composite ranking scores for members"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser: The argument parser instance.

        """
        parser.add_argument(
            "--user",
            type=str,
            help="Specific user login to process",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        user_login = options.get("user")
        calculator = MemberScoreCalculator()

        if user_login:
            users = User.objects.filter(login=user_login)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Member '{user_login}' not found"))
                return
        else:
            users = User.objects.all()

        total_users = users.count()
        self.stdout.write(f"Calculating scores for {total_users} members...")

        updated_users = []
        for idx, user in enumerate(users.iterator(chunk_size=BATCH_SIZE)):
            user.calculated_score = calculator.calculate(user)
            updated_users.append(user)

            if len(updated_users) >= BATCH_SIZE:
                User.bulk_save(updated_users, fields=("calculated_score",))
                self.stdout.write(f"  Processed {idx + 1} of {total_users}")
                updated_users = []

        User.bulk_save(updated_users, fields=("calculated_score",))

        self.stdout.write(
            self.style.SUCCESS(f"Successfully calculated scores for {total_users} members")
        )
