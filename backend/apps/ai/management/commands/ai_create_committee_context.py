"""A command to update context for OWASP committee data."""

from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_committee_content
from apps.ai.common.utils import create_context
from apps.owasp.models.committee import Committee


class Command(BaseCommand):
    help = "Update context for OWASP committee data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--committee-key",
            type=str,
            help="Process only the committee with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the committees",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of committees to process in each batch",
        )

    def handle(self, *args, **options):
        if options["committee_key"]:
            queryset = Committee.objects.filter(key=options["committee_key"])
        elif options["all"]:
            queryset = Committee.objects.all()
        else:
            queryset = Committee.objects.filter(is_active=True)

        if not (total_committees := queryset.count()):
            self.stdout.write("No committees found to process")
            return

        self.stdout.write(f"Found {total_committees} committees to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_committees, batch_size):
            batch_committees = queryset[offset : offset + batch_size]
            processed_count += self.process_context_batch(batch_committees)

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed processing {processed_count}/{total_committees} committees"
            )
        )

    def process_context_batch(self, committees: list[Committee]) -> int:
        """Process a batch of committees to create contexts."""
        processed = 0

        for committee in committees:
            prose_content, metadata_content = extract_committee_content(committee)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content for committee {committee.key}")
                continue

            if create_context(
                content=full_content, content_object=committee, source="owasp_committee"
            ):
                processed += 1
                self.stdout.write(f"Created context for {committee.key}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create context for {committee.key}")
                )
        return processed
