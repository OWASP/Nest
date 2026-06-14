"""Command to recalculate contributor scores."""

from django.core.management.base import BaseCommand, CommandError

from apps.owasp.score_calculator import ContributionScoreCalculator


class Command(BaseCommand):
    """Management command for recalculating contributor scores."""

    help = "Recalculate contributor scores and tier assignments."

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        self.stdout.write("Starting score recalculation for all users...")

        calculator = ContributionScoreCalculator()
        result = calculator.recalculate_all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Score recalculation complete:\n"
                f"  - Total users: {result['total']}\n"
                f"  - Created: {result['created']}\n"
                f"  - Updated: {result['updated']}\n"
                f"  - Failed: {result['failed_count']}"
            )
        )

        failed_count = result.get("failed_count", 0)
        if failed_count > 0:
            failures = result.get("failures", [])
            failed_users = [username for username, _ in failures]
            failed_str = ", ".join(failed_users)
            self.stdout.write(
                self.style.WARNING(f"Failed to issue certificates for: {failed_str}")
            )
            error_msg = f"Failed to issue certificates for {failed_count} user(s)"
            raise CommandError(error_msg)
