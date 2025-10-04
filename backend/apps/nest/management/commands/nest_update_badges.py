"""Management command to sync badges for users based on their roles/attributes."""

import logging

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.nest.models.badge import Badge
from apps.nest.models.user_badge import UserBadge

logger = logging.getLogger(__name__)

OWASP_STAFF_BADGE_NAME = "OWASP Staff"
WASPY_AWARD_BADGE_NAME = "WASPY Award Winner"


class Command(BaseCommand):
    """Sync badges for users based on their roles and attributes."""

    help = "Sync badges for users based on their roles and attributes"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Syncing user badges...")
        self.update_owasp_staff_badge()
        self.update_waspy_award_badge()
        self.stdout.write(self.style.SUCCESS("User badges sync completed"))

    def update_owasp_staff_badge(self):
        """Sync OWASP Staff badge for users."""
        # Get or create the OWASP Staff badge
        badge, created = Badge.objects.get_or_create(
            name=OWASP_STAFF_BADGE_NAME,
            defaults={
                "description": "Official OWASP Staff",
                "css_class": "fa-user-shield",
                "weight": 100,  # High weight for importance
            },
        )

        if created:
            logger.info("Created '%s' badge", OWASP_STAFF_BADGE_NAME)
            self.stdout.write(f"Created badge: {badge.name}")

        # Assign badge to employees who don't have it.
        employees_missing_or_inactive = User.objects.filter(is_owasp_staff=True).exclude(
            badges__badge=badge, badges__is_active=True
        )
        count = employees_missing_or_inactive.count()

        if count:
            for user in employees_missing_or_inactive:
                user_badge, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
                if not user_badge.is_active:
                    user_badge.is_active = True
                    user_badge.save(update_fields=["is_active"])

        logger.info("Added '%s' badge to %s users", OWASP_STAFF_BADGE_NAME, count)
        self.stdout.write(f"Added badge to {count} employees")

        # Remove badge from non-OWASP employees.
        non_employees = User.objects.filter(
            is_owasp_staff=False,
            user_badges__badge=badge,
        ).distinct()
        removed_count = non_employees.count()

        if removed_count:
            UserBadge.objects.filter(
                user_id__in=non_employees.values_list("id", flat=True),
                badge=badge,
            ).update(is_active=False)

        logger.info("Removed '%s' badge from %s users", OWASP_STAFF_BADGE_NAME, removed_count)
        self.stdout.write(f"Removed badge from {removed_count} non-employees")

    def update_waspy_award_badge(self):
        """Sync WASPY Award Winner badge for users."""
        # Get or create the WASPY Award Winner badge
        badge, created = Badge.objects.get_or_create(
            name=WASPY_AWARD_BADGE_NAME,
            defaults={
                "description": "WASPY Award Winner",
                "css_class": "fa-trophy",
                "weight": 90,
            },
        )

        if created:
            logger.info("Created '%s' badge", WASPY_AWARD_BADGE_NAME)
            self.stdout.write(f"Created badge: {badge.name}")

        # Get users with WASPY awards that have been reviewed
        waspy_award_users = User.objects.filter(
            awards__category="WASPY", awards__is_reviewed=True
        ).distinct()

        # Assign badge to WASPY award winners who don't have it
        users_missing_or_inactive = waspy_award_users.exclude(
            badges__badge=badge, badges__is_active=True
        )
        count = users_missing_or_inactive.count()

        if count:
            for user in users_missing_or_inactive:
                user_badge, _ = UserBadge.objects.get_or_create(user=user, badge=badge)
                if not user_badge.is_active:
                    user_badge.is_active = True
                    user_badge.save(update_fields=["is_active"])

        logger.info("Added '%s' badge to %s users", WASPY_AWARD_BADGE_NAME, count)
        self.stdout.write(f"Added badge to {count} WASPY award winners")

        # Remove badge from users who no longer have reviewed WASPY awards
        non_waspy_users = (
            User.objects.exclude(awards__category="WASPY", awards__is_reviewed=True)
            .filter(badges__badge=badge)
            .distinct()
        )
        removed_count = non_waspy_users.count()

        if removed_count:
            UserBadge.objects.filter(
                user_id__in=non_waspy_users.values_list("id", flat=True),
                badge=badge,
            ).update(is_active=False)

        logger.info("Removed '%s' badge from %s users", WASPY_AWARD_BADGE_NAME, removed_count)
        self.stdout.write(f"Removed badge from {removed_count} users without WASPY awards")
