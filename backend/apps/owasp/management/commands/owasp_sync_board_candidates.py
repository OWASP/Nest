"""A command to sync board candidates from www-board-candidates repository."""

import json
import re

import yaml
import yaml.scanner
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember


class Command(BaseCommand):
    help = "Sync board election candidates from www-board-candidates repository"

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--year",
            type=int,
            required=False,
            help="Specific year to sync (e.g., 2024). If not provided, syncs all years.",
        )

    def get_candidate_name_from_filename(self, filename: str) -> str:
        """Extract candidate name from filename.

        Args:
            filename (str): The candidate markdown filename.

        Returns:
            str: The extracted and formatted candidate name.

        """
        return filename.replace(".md", "").replace("-", " ").replace("_", " ").title()

    def parse_candidate_metadata(self, content: str) -> dict:
        """Parse YAML frontmatter from candidate markdown file.

        Args:
            content (str): The markdown file content.

        Returns:
            dict: Parsed metadata dictionary.

        """
        yaml_pattern = re.compile(r"^---\s*\n((?:(?!^---\s*$).*\n)+)^---\s*$", re.MULTILINE)

        if not content.startswith("---"):
            return {}

        try:
            if match := yaml_pattern.search(content):
                metadata_yaml = match.group(1)
                return yaml.safe_load(metadata_yaml) or {}
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            return {}

        return {}

    def sync_year_candidates(self, year: int) -> int:
        """Sync candidates for a specific year.

        Args:
            year (int): The election year to sync.

        Returns:
            int: Number of candidates synced.

        """
        board, _ = BoardOfDirectors.objects.get_or_create(year=year)
        content_type = ContentType.objects.get_for_model(BoardOfDirectors)

        repo_url = f"https://api.github.com/repos/OWASP/www-board-candidates/contents/{year}"

        try:
            candidates_content = get_repository_file_content(repo_url)
            files = json.loads(candidates_content)
        except (json.JSONDecodeError, OSError) as e:
            self.stderr.write(self.style.WARNING(f"Could not fetch candidates for {year}: {e}"))
            return 0

        synced_count = 0
        for file_info in files:
            filename = file_info.get("name", "")
            if not filename.endswith(".md"):
                continue

            if filename.lower() == "info.md":
                continue

            download_url = file_info.get("download_url")
            if not download_url:
                continue

            file_content = get_repository_file_content(download_url)
            metadata = self.parse_candidate_metadata(file_content)

            candidate_name = (
                metadata.get("name")
                or metadata.get("title")
                or self.get_candidate_name_from_filename(filename)
            )

            if not candidate_name:
                self.stderr.write(
                    self.style.WARNING(f"Skipping {filename}: No candidate name found")
                )
                continue

            data = {
                "entity_type": content_type,
                "entity_id": board.id,
                "member_name": candidate_name,
                "member_email": metadata.get("email", ""),
                "role": EntityMember.Role.CANDIDATE,
                "description": metadata.get("title", ""),
                "is_active": True,
                "is_reviewed": False,
                "order": 0,
            }

            EntityMember.update_data(data, save=True)
            synced_count += 1

        return synced_count

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        year = options.get("year")

        if year:
            count = self.sync_year_candidates(year)
            self.stdout.write(self.style.SUCCESS(f"Synced {count} candidates for {year}"))
        else:
            total_count = 0
            repo_url = "https://api.github.com/repos/OWASP/www-board-candidates/contents/"

            try:
                content = get_repository_file_content(repo_url)
                items = json.loads(content)
                years = [
                    int(item["name"])
                    for item in items
                    if item.get("type") == "dir" and item.get("name", "").isdigit()
                ]
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                self.stderr.write(self.style.ERROR(f"Could not fetch repository structure: {e}"))
                return

            for yr in sorted(years):
                count = self.sync_year_candidates(yr)
                total_count += count
                self.stdout.write(self.style.SUCCESS(f"Synced {count} candidates for {yr}"))

            self.stdout.write(
                self.style.SUCCESS(
                    f"Total: Synced {total_count} candidates across {len(years)} years"
                )
            )
