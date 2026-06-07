"""Command to recalculate contributor scores."""

from django.core.management.base import BaseCommand

from apps.owasp.score_calculator import ContributionScoreCalculator


class Command(BaseCommand):
    """Management command for recalculating contributor scores."""

    help = "Recalculate contributor scores and tier assignments."

    def handle(self, *_args, **options) -> None:
        """Handle the command execution."""
        calculator = ContributionScoreCalculator()
        self._recalculate_all_users(calculator)

    def _recalculate_all_users(self, calculator: ContributionScoreCalculator) -> None:
        """Recalculate scores for all users."""
        self.stdout.write("Starting score recalculation for all users...")

        result = calculator.recalculate_all_scores()

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Score recalculation complete:\n"
                f"  - Total users: {result['total']}\n"
                f"  - Created: {result['created']}\n"
                f"  - Updated: {result['updated']}"
            )
        )
