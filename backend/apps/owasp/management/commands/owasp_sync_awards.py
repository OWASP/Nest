"""A command to sync OWASP awards."""

import logging

import yaml
from django.core.management.base import BaseCommand

from apps.github.models.user import User
from apps.github.utils import get_repository_file_content
from apps.owasp.models.award import Award

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import awards from the OWASP awards YAML file"

    def handle(self, *args, **kwargs) -> None:
        """Handle the command execution."""
        self.stdout.write("Syncing OWASP awards...")

        data = yaml.safe_load(
            get_repository_file_content(
                "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/awards.yml"
            )
        )

        awards_to_save = []
        for item in data:
            if item.get("type") == "award":
                winners = item.get("winners", [])
                for winner in winners:
                    award = self._create_or_update_award(item, winner)
                    if award:
                        awards_to_save.append(award)

        Award.bulk_save(awards_to_save)
        self.stdout.write(self.style.SUCCESS(f"Successfully synced {len(awards_to_save)} awards"))

    def _create_or_update_award(self, award_data, winner_data):
        """Create or update award instance."""
        name = f"{award_data['title']} - {winner_data['name']} ({award_data['year']})"

        try:
            award = Award.objects.get(name=name)
        except Award.DoesNotExist:
            award = Award(name=name)

        award.category = award_data.get("category", "")
        award.description = winner_data.get("info", "")
        award.year = award_data.get("year", 0)

        # Try to match user by name
        user = self._match_user(winner_data["name"])
        if user:
            award.user = user
        else:
            logger.warning("Could not match user for award winner: %s", winner_data["name"])

        return award

    def _match_user(self, winner_name):
        """Try to match award winner with existing user."""
        # Try exact name match first
        user = User.objects.filter(name__iexact=winner_name).first()
        if user:
            return user

        # Try login match (GitHub username)
        user = User.objects.filter(login__iexact=winner_name).first()
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
