"""OWASP Board of Directors members sync command."""

import logging
from typing import Any, Dict, List, Optional

import requests
import yaml
from thefuzz import fuzz

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import models, transaction

from apps.github.models.user import User
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember

logger = logging.getLogger(__name__)

BOARD_HISTORY_URL = "https://raw.githubusercontent.com/OWASP/www-board/master/_data/board-history.yml"


class Command(BaseCommand):
    """Command to sync OWASP Board of Directors members."""

    help = "Sync OWASP Board of Directors members from www-board repository"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--year",
            type=int,
            help="Specific year to sync board members for",
            required=True,
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle command execution."""
        year = options["year"]

        self.stdout.write("Fetching OWASP Board of Directors data...")
        try:
            response = requests.get(BOARD_HISTORY_URL, timeout=15)
            response.raise_for_status()
            board_data = yaml.safe_load(response.text)
        except (requests.RequestException, yaml.YAMLError) as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to fetch or parse board history: {str(e)}")
            )
            return

        board_members = self._extract_board_members_for_year(board_data, year)
        if not board_members:
            self.stderr.write(
                self.style.ERROR(f"No board members found for year {year}")
            )
            return

        self.stdout.write(f"Processing {len(board_members)} board members for year {year}...")
        
        board, created = BoardOfDirectors.objects.get_or_create(year=year)
        if created:
            self.stdout.write(f"Created new BoardOfDirectors for year {year}")

        entity_type = ContentType.objects.get_for_model(BoardOfDirectors)
        processed_count = 0

        with transaction.atomic():
            for member_data in board_members:
                self._create_or_update_member(
                    member_data, board, entity_type
                )
                processed_count += 1
                if processed_count % 10 == 0:  # Show progress every 10 members
                    self.stdout.write(f"Processed {processed_count} of {len(board_members)} members")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully synced {processed_count} board members for year {year}")
        )

    def _extract_board_members_for_year(
        self, board_data: List[Dict[str, Any]], year: int
    ) -> List[Dict[str, str]]:
        """Extract board members for a specific year from board history data."""
        # Find the entry for the specified year
        year_entry = next(
            (entry for entry in board_data if entry.get("year") == year),
            None
        )

        if not year_entry:
            return []

        members = year_entry.get("members", [])
        return members

    def _create_or_update_member(
        self,
        member_data: Dict[str, str],
        board: BoardOfDirectors,
        entity_type: ContentType,
    ) -> None:
        """Create or update an EntityMember for a board member."""
        member_name = member_data.get("name", "").strip()
        if not member_name:
            logger.warning("Skipping member with empty name")
            return

        data = {
            "entity_id": board.id,
            "entity_type": entity_type,
            "member_name": member_name,
            "role": EntityMember.Role.MEMBER,
        }

        matched_user = self._fuzzy_match_github_user(member_name)
        if matched_user:
            data["member"] = matched_user

        try:
            entity_member = EntityMember.update_data(data, save=True)
            updates: list[str] = []
            if not entity_member.is_active:
                entity_member.is_active = True
                updates.append("is_active")
            if matched_user and entity_member.member_id != matched_user.id:
                entity_member.member = matched_user
                updates.append("member")
            if updates:
                entity_member.save(update_fields=updates)
            logger.info("Processed board member: %s", member_name)
        except Exception as e:
            logger.error("Failed to process board member %s: %s", member_name, str(e))

    def _fuzzy_match_github_user(self, member_name: str) -> User | None:
        """Attempt to fuzzy match a board member name with a GitHub user."""
        try:
            if not member_name:
                return None

            exact_match = User.objects.filter(name__iexact=member_name).first()
            if exact_match:
                return exact_match

            first_name = member_name.split()[0].lower()
            first_letter = first_name[0] if first_name else None

            if not first_letter:
                return None

            candidate_users = User.objects.filter(
                models.Q(name__istartswith=first_letter) |
                models.Q(name__icontains=f" {first_name} ") |  
                models.Q(name__istartswith=first_name + " ") |  
                models.Q(name__iendswith=" " + first_name)  
            ).exclude(name="")  

            if candidate_users.count() > 100: 
                candidate_users = candidate_users.filter(
                    models.Q(name__istartswith=first_name + " ") |
                    models.Q(name__icontains=f" {first_name} ")
                )

            SIMILARITY_THRESHOLD = 80  
            potential_matches = []
            
            for user in candidate_users:
                similarity = fuzz.ratio(member_name.lower(), user.name.lower())
                if similarity >= SIMILARITY_THRESHOLD:
                    potential_matches.append((user, similarity))
            
            if potential_matches:
                best_match = max(potential_matches, key=lambda x: x[1])
                logger.info(
                    "Found fuzzy match for %s: %s (similarity: %d%%)",
                    member_name,
                    best_match[0].name,
                    best_match[1]
                )
                return best_match[0]
                
            return None
            
        except Exception as e:
            logger.warning("Failed to match GitHub user for %s: %s", member_name, str(e))
            return None
