"""A command to generate board candidates' claims using www-board-candidates repository."""

import json
import unicodedata

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from apps.ai.common.utils import extract_json_from_markdown
from apps.common.open_ai import OpenAi
from apps.github.utils import get_repository_file_content
from apps.owasp.models.board_candidate_claim import BoardCandidateClaim
from apps.owasp.models.board_of_directors import BoardOfDirectors
from apps.owasp.models.entity_member import EntityMember

PROMPT_EXTRACT_CLAIMS = """
You are an expert at extracting verifiable, actionable claims from board candidate statements.
Analyze the provided markdown content of a candidate's statement.
Extract specific, verifiable claims made by the candidate.

CRITICAL RULES:
1. ONLY extract historical facts, past achievements, and current established roles
(e.g., "Founded OWASP Nest", "Co-leader of Nettacker").
2. DO NOT extract future plans, 90-day goals, campaign promises,
or things the candidate "plans to do" (e.g., ignore "Finish OWASP Nest API",
 "Launch Mentorship Portal", "Advocate for resources").
3. You may receive multiple statements from different years for the same candidate.
You MUST synthesize this information and ensure you do not extract duplicate
or highly overlapping claims.
4. Phrase the statements in third person.
5. Include impressive achievements, statements, and quantifiable information.
6. Avoid using the name or any pronouns.

Return ONLY a valid JSON array of objects.
Each object must have exactly two keys:
  - "name": A concise 10-20 word summary of the claim.
  - "description": The full contextual text of the claim.
"""


class Command(BaseCommand):
    help = "Generate board election candidates' claims from www-board-candidates repository"

    def add_arguments(self, parser):
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "--source-years",
            type=int,
            nargs="+",
            required=True,
            help="List of years to fetch candidate's markdown files for (e.g., 2025).",
        )
        parser.add_argument(
            "--year",
            type=int,
            required=True,
            help="Target election year in the database to assign the claims to.",
        )
        parser.add_argument(
            "--name",
            type=str,
            required=False,
            help="Optional full name to filter for a specific candidate (e.g. 'John Doe'.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Generate claims and print them to the console without saving to the database.",
        )

    def get_filename_from_candidate_name(self, candidate_name: str, source_year: int) -> str:
        """Derive markdown filename from candidate name.

        Args:
            candidate_name (str): The candidate's full name.
            source_year (int): The election year.

        Returns:
            str: The derived markdown filename.

        """
        base_name = (
            unicodedata.normalize("NFKD", candidate_name)
            .encode("ascii", "ignore")
            .decode("ascii")
            .lower()
            .replace("'", "")
            .replace(".", "")
            .replace(" ", "_")
            .replace("-", "_")
        )

        # Year 2022 markdown files have a "_2022" suffix.
        exception_year = 2022
        if source_year == exception_year:
            return f"{base_name}_{exception_year}.md"

        return f"{base_name}.md"

    def generate_claims(
        self, markdown_content: str, candidate: EntityMember, board: BoardOfDirectors
    ) -> list[BoardCandidateClaim]:
        """Generate draft BoardCandidateClaim objects from candidate markdown using AI.

        Args:
            markdown_content (str): The markdown text of the candidate's statement.
            candidate (EntityMember): The candidate entity member.
            board (BoardOfDirectors): The board of directors election year.

        Returns:
            list[BoardCandidateClaim]: A list of unsaved draft claim objects.

        """
        open_ai = OpenAi(max_tokens=2000)
        response = open_ai.set_prompt(PROMPT_EXTRACT_CLAIMS).set_input(markdown_content).complete()

        if not response:
            return []

        cleaned_response = extract_json_from_markdown(response)

        try:
            claims_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to parse JSON for candidate {candidate.member_name}: {e}"
                )
            )
            return []

        if not isinstance(claims_data, list):
            self.stderr.write(
                self.style.ERROR(
                    f"Expected a list of claims for {candidate.member_name}, "
                    f"got {type(claims_data)}"
                )
            )
            return []

        claims = []
        for claim_data in claims_data:
            if not isinstance(claim_data, dict):
                continue

            name = str(claim_data.get("name") or "").strip()[
                : BoardCandidateClaim._meta.get_field("name").max_length
            ]
            description = str(claim_data.get("description") or "").strip()

            if name:
                claims.append(
                    BoardCandidateClaim(
                        board=board,
                        description=description,
                        candidate=candidate,
                        name=name,
                        status=BoardCandidateClaim.Status.DRAFT,
                    )
                )

        return claims

    def handle(self, *args, **options):
        """Handle the command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        source_years = options["source_years"]
        year = options["year"]
        name = options.get("name")
        dry_run = options.get("dry_run", False)

        try:
            board = BoardOfDirectors.objects.get(year=year)
        except BoardOfDirectors.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Board of Directors for year {year} not found."))
            return

        content_type = ContentType.objects.get_for_model(BoardOfDirectors)
        candidates = EntityMember.objects.filter(
            entity_type=content_type,
            entity_id=board.id,
            role=EntityMember.Role.CANDIDATE,
        )

        if name:
            candidates = candidates.filter(member_name__iexact=name)

        if not candidates.exists():
            self.stderr.write(self.style.WARNING("No candidates found matching the criteria."))
            return

        processed_count = 0
        for candidate in candidates:
            try:
                if (
                    not dry_run
                    and BoardCandidateClaim.objects.filter(candidate=candidate).exists()
                ):
                    self.stdout.write(
                        f"Claims already exist for {candidate.member_name}, skipping..."
                    )
                    continue

                aggregated_texts = []
                for source_year in source_years:
                    filename = self.get_filename_from_candidate_name(
                        candidate.member_name, source_year
                    )
                    url = (
                        "https://raw.githubusercontent.com/OWASP/www-board-candidates/"
                        f"master/{source_year}/{filename}"
                    )

                    content = get_repository_file_content(url)
                    if content and "404: Not Found" not in content[:30]:
                        aggregated_texts.append(content)

                if not aggregated_texts:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Could not find any markdown files for {candidate.member_name} "
                            f"in source years {source_years}"
                        )
                    )
                    continue

                self.stdout.write(f"Generating claims for {candidate.member_name}...")
                file_content = "\n\n--- Next Statement ---\n\n".join(aggregated_texts)

                claims = self.generate_claims(file_content, candidate, board)
                if not claims:
                    self.stderr.write(
                        self.style.ERROR(f"Failed to generate claims for {candidate.member_name}.")
                    )
                    continue

                seen_names = set()
                unique_claims = []
                for claim in claims:
                    if claim.name not in seen_names:
                        seen_names.add(claim.name)
                        unique_claims.append(claim)
                claims = unique_claims

                saved_count = 0
                failed_count = 0
                for claim in claims:
                    if dry_run:
                        self.stdout.write(
                            f"[DRY RUN] Generated Claim:\n  "
                            f"Name: {claim.name}\n  Desc: {claim.description}\n"
                        )
                    else:
                        try:
                            claim.save()
                            saved_count += 1
                        except (IntegrityError, ValidationError) as e:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"Failed to save claim '{claim.name}' for "
                                    f"{candidate.member_name}: {e}"
                                )
                            )
                            failed_count += 1
                        except Exception as e:  # noqa: BLE001
                            self.stderr.write(
                                self.style.ERROR(
                                    f"Unexpected error saving claim '{claim.name}' for "
                                    f"{candidate.member_name}: {e}"
                                )
                            )
                            failed_count += 1

                processed_count += 1
                failed_suffix = f", {failed_count} failed" if failed_count else ""
                msg = f"Saved {saved_count} claims for {candidate.member_name}{failed_suffix}"
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"[DRY RUN] Would have saved claims for {candidate.member_name}"
                        )
                    )
                elif saved_count:
                    self.stdout.write(self.style.SUCCESS(msg))
                else:
                    self.stderr.write(self.style.ERROR(msg))
            except Exception as e:  # noqa: BLE001
                self.stderr.write(
                    self.style.ERROR(f"Failed to process candidate {candidate.member_name}: {e}")
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"[DRY RUN] Finished processing {processed_count} candidates.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Finished generating claims for {processed_count} candidates.")
            )
