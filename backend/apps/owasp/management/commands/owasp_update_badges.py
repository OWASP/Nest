"""Update user badges based on OWASP awards."""

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.owasp.models.award import Award


class Command(BaseCommand):
    """Update user badges based on OWASP awards."""

    help = "Update user badges based on OWASP awards"

    def handle(self, *args, **options):
        """Handle the command execution."""
        # Get or create WASPY badge
        waspy_badge, created = Badge.objects.get_or_create(
            name="WASPY Award Winner",
            defaults={
                "description": "Recipient of WASPY award from OWASP",
                "css_class": "badge-waspy",
                "weight": 10,
            },
        )

        if created:
            self.stdout.write(f"Created badge: {waspy_badge.name}")

        # Get users with WASPY awards using the model method
        waspy_winners = Award.get_waspy_award_winners()
        waspy_winner_ids = set(waspy_winners.values_list("id", flat=True))
        waspy_winners_count = len(waspy_winner_ids)

        # Add badge to WASPY winners
        for user in waspy_winners:
            user.badges.add(waspy_badge)

        # Remove badge from users no longer on the WASPY winners list
        users_with_badge = User.objects.filter(badges=waspy_badge)

        for user in users_with_badge:
            if user.id not in waspy_winner_ids:
                user.badges.remove(waspy_badge)

        self.stdout.write(f"Updated badges for {waspy_winners_count} WASPY winners")
