"""A command to link issues to mentorship modules based on matching labels."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.github.models.issue import Issue
from apps.mentorship.models.module import Module


class Command(BaseCommand):
    """Efficiently link issues to mentorship modules based on matching labels."""

    help = "Efficiently link issues to mentorship modules based on matching labels."

    def handle(self, *_args, **options) -> None:
        """Handle the command execution.

        Args:
            *_args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        self.stdout.write("Fetching all issues and labels...")
        # load id
        issues = Issue.objects.prefetch_related("labels").only("id")

        label_to_issue_ids: dict[str, set[int]] = {}
        for issue in issues:
            for label in issue.labels.all():
                label_to_issue_ids.setdefault(label.name, set()).add(issue.id)

        total_modules = 0
        total_links = 0

        self.stdout.write("Processing modules...")
        # Filter out modules without linked_issue_labels upfront
        modules = (
            Module.objects.exclude(linked_issue_labels__isnull=True)
            .exclude(linked_issue_labels=[])
            .iterator()
        )

        for module in modules:
            linked_labels = module.linked_issue_labels

            matched_issue_ids = set()
            for label in linked_labels:
                matched_issue_ids.update(label_to_issue_ids.get(label, set()))

            if matched_issue_ids:
                current_ids = set(module.linked_issues.values_list("id", flat=True))
                if current_ids != matched_issue_ids:
                    with transaction.atomic():
                        module.linked_issues.set(matched_issue_ids)
                    total_links += len(matched_issue_ids)
                    total_modules += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Linked {len(matched_issue_ids)} issues to module '{module.name}'"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. {total_links} issues linked across {total_modules} modules."
            )
        )
