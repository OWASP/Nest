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

        # Get users with reviewed WASPY awards only
        waspy_winners = User.objects.filter(
            awards__category=Award.Category.WASPY, awards__is_reviewed=True
        ).distinct()

        # Add badge to WASPY winners
        for user in waspy_winners:
            user.badges.add(waspy_badge)

        # Remove badge from users without reviewed WASPY awards
        users_with_badge = User.objects.filter(badges=waspy_badge)
        for user in users_with_badge:
            if not Award.objects.filter(
                user=user, category=Award.Category.WASPY, is_reviewed=True
            ).exists():
                user.badges.remove(waspy_badge)

        self.stdout.write(f"Updated badges for {waspy_winners.count()} WASPY winners")
