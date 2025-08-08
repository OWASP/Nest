"""A command to update user badges based on awards and other achievements."""

import logging

from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.nest.models.badge import BadgeType, UserBadge
from apps.owasp.models.award import Award

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Update user badges based on awards and achievements."""

    help = "Update user badges based on OWASP awards and other achievements"

    def __init__(self, *args, **kwargs):
        """Initialize the command with counters for tracking changes."""
        super().__init__(*args, **kwargs)
        self.badges_created = 0
        self.badges_removed = 0
        self.users_processed = 0

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes to the database",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose logging",
        )
        parser.add_argument(
            "--user-login",
            type=str,
            help="Process badges for a specific user (by GitHub login)",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        if options["verbose"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write("Starting user badges update...")

        try:
            # Ensure badge types exist
            self._ensure_badge_types_exist(dry_run=options["dry_run"])

            # Process users
            if options["user_login"]:
                self._process_single_user(options["user_login"], dry_run=options["dry_run"])
            else:
                self._process_all_users(dry_run=options["dry_run"])

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.exception("Error updating user badges")
            self.stdout.write(self.style.ERROR(f"Error updating user badges: {e!s}"))

    def _ensure_badge_types_exist(self, *, dry_run: bool = False):
        """Ensure required badge types exist in the database."""
        badge_types = [
            {
                "name": "WASPY Award Winner",
                "description": "Awarded to users who have received any WASPY award from OWASP",
                "icon": "🏆",
                "color": "#FFD700",
            },
            # Add more badge types here as needed
        ]

        for badge_data in badge_types:
            if not dry_run:
                badge_type, created = BadgeType.objects.get_or_create(
                    name=badge_data["name"],
                    defaults={
                        "description": badge_data["description"],
                        "icon": badge_data["icon"],
                        "color": badge_data["color"],
                        "is_active": True,
                    },
                )
                if created:
                    logger.debug("Created badge type: %s", badge_type.name)
                else:
                    # Update existing badge type
                    badge_type.description = badge_data["description"]
                    badge_type.icon = badge_data["icon"]
                    badge_type.color = badge_data["color"]
                    badge_type.save(
                        update_fields=["description", "icon", "color", "nest_updated_at"]
                    )
                    logger.debug("Updated badge type: %s", badge_type.name)
            else:
                logger.debug("[DRY RUN] Would ensure badge type exists: %s", badge_data["name"])

    def _process_all_users(self, *, dry_run: bool = False):
        """Process badges for all users."""
        # Get all users who have awards or existing badges
        users_with_awards = set(
            Award.objects.filter(user__isnull=False).values_list("user_id", flat=True).distinct()
        )

        users_with_badges = set(UserBadge.objects.values_list("user_id", flat=True).distinct())

        all_user_ids = users_with_awards | users_with_badges

        if not all_user_ids:
            self.stdout.write("No users found with awards or badges to process.")
            return

        users = User.objects.filter(id__in=all_user_ids).prefetch_related("awards", "badges")

        for user in users:
            self._process_user_badges(user, dry_run=dry_run)
            self.users_processed += 1

    def _process_single_user(self, user_login: str, *, dry_run: bool = False):
        """Process badges for a single user."""
        try:
            user = User.objects.prefetch_related("awards", "badges").get(login=user_login)
            self._process_user_badges(user, dry_run=dry_run)
            self.users_processed += 1
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with login '{user_login}' not found"))

    def _process_user_badges(self, user: User, *, dry_run: bool = False):
        """Process badges for a specific user."""
        logger.debug("Processing badges for user: %s", user.login)

        # Process WASPY Award Winner badge
        self._process_waspy_award_badge(user, dry_run=dry_run)

        # Add more badge processing logic here as needed

    def _process_waspy_award_badge(self, user: User, *, dry_run: bool = False):
        """Process WASPY Award Winner badge for a user."""
        badge_name = "WASPY Award Winner"

        # Check if user has any WASPY awards
        waspy_awards = user.awards.filter(category="WASPY", award_type="award")

        has_waspy_award = waspy_awards.exists()

        if not dry_run:
            try:
                badge_type = BadgeType.objects.get(name=badge_name)
            except BadgeType.DoesNotExist:
                logger.exception("Badge type '%s' not found", badge_name)
                return

            # Check if user already has this badge
            existing_badge = UserBadge.objects.filter(user=user, badge_type=badge_type).first()

            if has_waspy_award and not existing_badge:
                # Award the badge
                award_details = [
                    {
                        "award_name": award.name,
                        "year": award.year,
                        "winner_name": award.winner_name,
                    }
                    for award in waspy_awards
                ]

                award_names_str = ", ".join(
                    [f"{a['award_name']} ({a['year']})" for a in award_details]
                )
                UserBadge.objects.create(
                    user=user,
                    badge_type=badge_type,
                    reason=f"Received WASPY award(s): {award_names_str}",
                    metadata={
                        "awards": award_details,
                        "award_count": len(award_details),
                    },
                )
                self.badges_created += 1
                logger.debug("Awarded '%s' badge to %s", badge_name, user.login)

            elif not has_waspy_award and existing_badge:
                # Remove the badge (award no longer associated)
                existing_badge.delete()
                self.badges_removed += 1
                logger.debug("Removed '%s' badge from %s", badge_name, user.login)

            elif has_waspy_award and existing_badge:
                # Update badge metadata if needed
                award_details = []
                for award in waspy_awards:
                    award_details.append(
                        {
                            "award_name": award.name,
                            "year": award.year,
                            "winner_name": award.winner_name,
                        }
                    )

                new_metadata = {
                    "awards": award_details,
                    "award_count": len(award_details),
                }

                if existing_badge.metadata != new_metadata:
                    award_names_str = ", ".join(
                        [f"{a['award_name']} ({a['year']})" for a in award_details]
                    )
                    existing_badge.metadata = new_metadata
                    existing_badge.reason = f"Received WASPY award(s): {award_names_str}"
                    existing_badge.save(update_fields=["metadata", "reason", "nest_updated_at"])
                    logger.debug("Updated '%s' badge metadata for %s", badge_name, user.login)

        # Dry run logging
        elif has_waspy_award:
            award_names = list(waspy_awards.values_list("name", "year"))
            logger.debug(
                "[DRY RUN] Would award/update '%s' badge to %s for awards: %s",
                badge_name,
                user.login,
                award_names,
            )
        else:
            logger.debug("[DRY RUN] Would check for badge removal for %s", user.login)

    def _print_summary(self):
        """Print command execution summary."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("User Badges Update Summary")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Users processed: {self.users_processed}")
        self.stdout.write(f"Badges created: {self.badges_created}")
        self.stdout.write(f"Badges removed: {self.badges_removed}")
        self.stdout.write("\nBadge update completed successfully!")
