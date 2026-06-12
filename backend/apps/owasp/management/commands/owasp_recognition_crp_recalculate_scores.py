"""Command to recalculate contributor scores."""

from django.core.management.base import BaseCommand

from apps.owasp.score_calculator import ContributionScoreCalculator


class Command(BaseCommand):
    """Management command for recalculating contributor scores."""

    help = "Recalculate contributor scores and tier assignments."

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        self.stdout.write("Starting score recalculation for all users...")

        calculator = ContributionScoreCalculator()
        result = calculator.recalculate_all_scores()

        self.stdout.write(
            self.style.SUCCESS(
                f"Score recalculation complete:\n"
                f"  - Total users: {result['total']}\n"
                f"  - Created: {result['created']}\n"
                f"  - Updated: {result['updated']}"
            )
        )
