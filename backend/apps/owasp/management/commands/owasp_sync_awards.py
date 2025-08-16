"""A command to sync OWASP awards from the canonical YAML source."""

import logging
import re

import yaml
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.github.models.user import User
from apps.github.utils import get_repository_file_content
from apps.owasp.models.award import Award

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Sync OWASP awards from the canonical YAML source."""

    help = "Sync OWASP awards from https://github.com/OWASP/owasp.github.io/blob/main/_data/awards.yml"

    def __init__(self, *args, **kwargs):
        """Initialize the command with counters for tracking sync progress."""
        super().__init__(*args, **kwargs)
        self.awards_created = 0
        self.awards_updated = 0
        self.users_matched = 0
        self.users_unmatched = 0
        self.unmatched_names = []

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

    def handle(self, *args, **options):
        """Handle the command execution."""
        if options["verbose"]:
            logger.setLevel(logging.DEBUG)

        self.stdout.write("Starting OWASP awards sync...")

        try:
            # Download and parse the awards YAML
            yaml_content = get_repository_file_content(
                "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/awards.yml"
            )

            if not yaml_content:
                self.stdout.write(self.style.ERROR("Failed to download awards.yml from GitHub"))
                return

            awards_data = yaml.safe_load(yaml_content)

            if not awards_data:
                self.stdout.write(self.style.ERROR("Failed to parse awards.yml content"))
                return

            # Process awards data
            if options["dry_run"]:
                self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
                self._process_awards_data(awards_data, dry_run=True)
            else:
                with transaction.atomic():
                    self._process_awards_data(awards_data, dry_run=False)

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.exception("Error syncing awards")
            self.stdout.write(self.style.ERROR(f"Error syncing awards: {e!s}"))

    def _process_awards_data(self, awards_data: list[dict], *, dry_run: bool = False):
        """Process the awards data from YAML."""
        for item in awards_data:
            if item.get("type") == "category":
                self._process_category(item, dry_run=dry_run)
            elif item.get("type") == "award":
                self._process_award(item, dry_run=dry_run)

    def _process_category(self, category_data: dict, *, dry_run: bool = False):
        """Process a category definition."""
        category_name = category_data.get("title", "")
        description = category_data.get("description", "")

        if not category_name:
            logger.warning("Skipping category with no title")
            return

        # Create or update category record
        if not dry_run:
            award, created = Award.objects.get_or_create(
                name=category_name,
                award_type="category",
                defaults={
                    "category": category_name,
                    "description": description,
                },
            )

            if created:
                self.awards_created += 1
                logger.debug("Created category: %s", category_name)
            else:
                # Update existing category
                award.description = description
                award.save(update_fields=["description", "nest_updated_at"])
                self.awards_updated += 1
                logger.debug("Updated category: %s", category_name)
        else:
            logger.debug("[DRY RUN] Would process category: %s", category_name)

    def _process_award(self, award_data: dict, *, dry_run: bool = False):
        """Process an individual award."""
        award_name = award_data.get("title", "")
        category = award_data.get("category", "")
        year = award_data.get("year")
        winners = award_data.get("winners", [])

        if not award_name or not category or not year:
            logger.warning("Skipping incomplete award: %s", award_data)
            return

        # Process each winner
        for winner_data in winners:
            self._process_winner(award_name, category, year, winner_data, dry_run=dry_run)

    def _process_winner(
        self,
        award_name: str,
        category: str,
        year: int,
        winner_data: dict,
        *,
        dry_run: bool = False,
    ):
        """Process an individual award winner."""
        winner_name = winner_data.get("name", "").strip()
        winner_info = winner_data.get("info", "")
        winner_image = winner_data.get("image", "")

        if not winner_name:
            logger.warning("Skipping winner with no name for award: %s", award_name)
            return

        # Try to match winner with existing user
        matched_user = self._match_user(winner_name, winner_info)

        if matched_user:
            self.users_matched += 1
            logger.debug("Matched user: %s -> %s", winner_name, matched_user.login)
        else:
            self.users_unmatched += 1
            self.unmatched_names.append(winner_name)
            logger.warning("Could not match user: %s", winner_name)

        if not dry_run:
            # Create or update award record
            award, created = Award.objects.get_or_create(
                name=award_name,
                category=category,
                year=year,
                winner_name=winner_name,
                defaults={
                    "award_type": "award",
                    "description": "",
                    "winner_info": winner_info,
                    "winner_image": winner_image,
                    "user": matched_user,
                },
            )

            if created:
                self.awards_created += 1
                logger.debug("Created award: %s for %s", award_name, winner_name)
            else:
                # Update existing award
                updated_fields = []
                if award.winner_info != winner_info:
                    award.winner_info = winner_info
                    updated_fields.append("winner_info")
                if award.winner_image != winner_image:
                    award.winner_image = winner_image
                    updated_fields.append("winner_image")
                if award.user != matched_user:
                    award.user = matched_user
                    updated_fields.append("user")

                if updated_fields:
                    updated_fields.append("nest_updated_at")
                    award.save(update_fields=updated_fields)
                    self.awards_updated += 1
                    logger.debug("Updated award: %s for %s", award_name, winner_name)
        else:
            logger.debug("[DRY RUN] Would process winner: %s for %s", winner_name, award_name)

    def _match_user(self, winner_name: str, winner_info: str = "") -> User | None:
        """Attempt to match a winner name with an existing GitHub user."""
        if not winner_name:
            return None

        # Constants for magic numbers
        min_name_parts = 2
        min_login_length = 2

        # Clean the winner name
        clean_name = winner_name.strip()

        # Try different matching strategies in order
        user = self._try_exact_name_match(clean_name)
        if user:
            return user

        user = self._try_github_username_match(winner_info)
        if user:
            return user

        user = self._try_fuzzy_name_match(clean_name, min_name_parts)
        if user:
            return user

        user = self._try_login_variations(clean_name, min_login_length)
        if user:
            return user

        return None

    def _try_exact_name_match(self, clean_name: str) -> User | None:
        """Try exact name matching."""
        try:
            return User.objects.get(name__iexact=clean_name)
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple users have the same name, try to find the most relevant one
            users = User.objects.filter(name__iexact=clean_name)
            # Prefer users with more contributions or followers
            return users.order_by("-contributions_count", "-followers_count").first()

    def _try_github_username_match(self, winner_info: str) -> User | None:
        """Try to extract GitHub username from winner_info."""
        github_username = self._extract_github_username(winner_info)
        if github_username:
            try:
                return User.objects.get(login__iexact=github_username)
            except User.DoesNotExist:
                pass
        return None

    def _try_fuzzy_name_match(self, clean_name: str, min_name_parts: int) -> User | None:
        """Try fuzzy name matching with partial matches."""
        name_parts = clean_name.split()
        if len(name_parts) >= min_name_parts:
            # Try "FirstName LastName" variations
            for i in range(len(name_parts)):
                for j in range(i + 1, len(name_parts) + 1):
                    partial_name = " ".join(name_parts[i:j])
                    try:
                        return User.objects.get(name__icontains=partial_name)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        continue
        return None

    def _try_login_variations(self, clean_name: str, min_login_length: int) -> User | None:
        """Try login field with name variations."""
        potential_logins = self._generate_potential_logins(clean_name, min_login_length)
        for login in potential_logins:
            try:
                return User.objects.get(login__iexact=login)
            except User.DoesNotExist:
                continue
        return None

    def _extract_github_username(self, text: str) -> str | None:
        """Extract GitHub username from text using various patterns."""
        if not text:
            return None

        # Pattern 1: github.com/username
        github_url_pattern = r"github\.com/([a-zA-Z0-9\-_]+)"
        match = re.search(github_url_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

        # Pattern 2: @username mentions
        mention_pattern = r"@([a-zA-Z0-9\-_]+)"
        match = re.search(mention_pattern, text)
        if match:
            return match.group(1)

        return None

    def _generate_potential_logins(self, name: str, min_login_length: int = 2) -> list[str]:
        """Generate potential GitHub login variations from a name."""
        if not name:
            return []

        potential_logins = []
        clean_name = re.sub(r"[^a-zA-Z0-9\s\-_]", "", name).strip()

        # Convert to lowercase and replace spaces
        base_variations = [
            clean_name.lower().replace(" ", ""),
            clean_name.lower().replace(" ", "-"),
            clean_name.lower().replace(" ", "_"),
        ]

        # Add variations with different cases
        for variation in base_variations:
            potential_logins.extend(
                [
                    variation,
                    variation.replace("-", ""),
                    variation.replace("_", ""),
                    variation.replace("-", "_"),
                    variation.replace("_", "-"),
                ]
            )

        # Remove duplicates while preserving order
        seen = set()
        unique_logins = []
        for login in potential_logins:
            if login and login not in seen and len(login) >= min_login_length:
                seen.add(login)
                unique_logins.append(login)

        return unique_logins[:10]  # Limit to avoid too many queries

    def _print_summary(self):
        """Print command execution summary."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("OWASP Awards Sync Summary")
        self.stdout.write("=" * 50)
        self.stdout.write(f"Awards created: {self.awards_created}")
        self.stdout.write(f"Awards updated: {self.awards_updated}")
        self.stdout.write(f"Users matched: {self.users_matched}")
        self.stdout.write(f"Users unmatched: {self.users_unmatched}")

        if self.unmatched_names:
            self.stdout.write(f"\nUnmatched winners ({len(self.unmatched_names)}):")
            for name in sorted(set(self.unmatched_names)):
                self.stdout.write(f"  - {name}")

        self.stdout.write("\nSync completed successfully!")
