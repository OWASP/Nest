"""A command to sync OWASP awards."""

import logging

import yaml
from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.github.utils import get_repository_file_content
from apps.owasp.models.award import Award

logger = logging.getLogger(__name__)

# Year validation constants
MIN_VALID_YEAR = 1900
MAX_VALID_YEAR = 2100


class Command(BaseCommand):
    help = "Import awards from the OWASP awards YAML file"

    def handle(self, *args, **kwargs) -> None:
        """Handle the command execution."""
        self.stdout.write("Syncing OWASP awards...")

        url = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/awards.yml"
        raw = get_repository_file_content(url)
        if not raw:
            self.stderr.write(self.style.WARNING("No awards data fetched; aborting."))
            return
        try:
            data = yaml.safe_load(raw) or []
        except yaml.YAMLError as e:
            self.stderr.write(self.style.ERROR(f"Failed to parse awards YAML: {e}"))
            return
        if not isinstance(data, list):
            self.stderr.write(
                self.style.WARNING("Unexpected awards YAML structure; expected a list.")
            )
            return

        awards_to_save = []
        skipped_count = 0
        for item in data:
            if item.get("type") == "award":
                winners = item.get("winners", [])
                for winner in winners:
                    award = self._create_or_update_award(item, winner)
                    if award:
                        awards_to_save.append(award)
                    else:
                        skipped_count += 1

        Award.bulk_save(awards_to_save, fields=("category", "description", "year", "user"))
        self.stdout.write(self.style.SUCCESS(f"Successfully synced {len(awards_to_save)} awards"))
        if skipped_count:
            self.stdout.write(
                self.style.WARNING(f"Skipped {skipped_count} awards due to invalid data")
            )

    def _create_or_update_award(self, award_data, winner_data):
        """Create or update award instance."""
        # Safely extract values with defaults
        title = award_data.get("title", "")
        category = award_data.get("category", "")

        # Validate and parse year
        try:
            year = int(award_data.get("year", 0))
            if year <= 0 or year < MIN_VALID_YEAR or year > MAX_VALID_YEAR:
                logger.warning("Invalid year %s for award %s, skipping", year, title)
                return None
        except (ValueError, TypeError):
            logger.warning(
                "Could not parse year %s for award %s, skipping", award_data.get("year"), title
            )
            return None

        # Handle winner_data being string or dict
        if isinstance(winner_data, str):
            winner_name = winner_data
            winner_info = ""
        else:
            # Prefer explicit GitHub login over name
            login = winner_data.get("login") or winner_data.get("github")
            if login:
                login = login.lstrip("@")
                # Skip bot accounts
                if "bot" in login.lower() or login.lower().endswith("[bot]"):
                    logger.warning("Skipping bot account: %s", login)
                    return None
                winner_name = login
            else:
                winner_name = winner_data.get("name", "")
            winner_info = winner_data.get("info", "")

        name = f"{title} - {winner_name} ({year})"

        try:
            award = Award.objects.get(name=name)
        except Award.DoesNotExist:
            award = Award(name=name)

        award.category = category
        award.description = winner_info
        award.year = year

        # Only set user if not already reviewed
        if not (award.user and award.is_reviewed):
            user = self._match_user(winner_name)
            if user:
                award.user = user
            else:
                logger.warning("Could not match user for award winner: %s", winner_name)

        return award

    def _match_user(self, winner_name):
        """Try to match award winner with existing user."""
        winner_name = winner_name.strip()

        # Check if it looks like a GitHub handle
        if winner_name.startswith("@") or (" " not in winner_name and winner_name):
            # Strip leading @ and try login match first
            login_name = winner_name.lstrip("@")
            user = User.objects.filter(login__iexact=login_name).first()
            if user:
                return user

        # Try exact name match
        user = User.objects.filter(name__iexact=winner_name).first()
        if user:
            return user

        # Try partial name match
        name_parts = winner_name.split()
        min_name_parts = 2
        if len(name_parts) >= min_name_parts:
            first_name, last_name = name_parts[0], name_parts[-1]
            user = (
                User.objects.filter(name__icontains=first_name)
                .filter(name__icontains=last_name)
                .first()
            )
            if user:
                return user

        return None
