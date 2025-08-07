"""A command to link issues to mentorship modules based on matching labels."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.github.models.issue import Issue
from apps.mentorship.models.module import Module


class Command(BaseCommand):
    """Efficiently link issues to mentorship modules based on matching labels."""

    help = (
        "Links issues to modules by matching labels from all repositories "
        "associated with the module's project."
    )

    def handle(self, *_args, **options) -> None:
        """Handle the command execution.

        Args:
            *_args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        # Build a Repository-Aware Map of Labels to Issues ---
        self.stdout.write("Building a repository-aware map of labels to issues...")
        repo_label_to_issue_ids: dict[tuple[int, str], set[int]] = {}

        issues_query = Issue.objects.select_related("repository").prefetch_related("labels")

        for issue in issues_query:
            if not issue.repository_id:
                continue

            for label in issue.labels.all():
                key = (issue.repository_id, label.name)
                repo_label_to_issue_ids.setdefault(key, set()).add(issue.id)

        self.stdout.write(
            f"Map built. Found issues for {len(repo_label_to_issue_ids)} unique repo-label pairs."
        )

        total_modules_updated = 0
        total_links_created = 0

        # Process modules and link issues from multiple repositories
        self.stdout.write("Processing modules and linking issues...")

        modules_to_process = (
            Module.objects.prefetch_related("project__repositories")
            .exclude(project__repositories__isnull=True)
            .exclude(labels__isnull=True)
            .exclude(labels=[])
        )

        for module in modules_to_process:
            project_repos = module.project.repositories.all()
            linked_label_names = module.labels

            matched_issue_ids = set()
            for repo in project_repos:
                for label_name in linked_label_names:
                    key = (repo.id, label_name)
                    issues_for_label = repo_label_to_issue_ids.get(key, set())
                    matched_issue_ids.update(issues_for_label)

            with transaction.atomic():
                module.issues.set(matched_issue_ids)

            num_linked = len(matched_issue_ids)
            total_links_created += num_linked
            total_modules_updated += 1

            repo_names = ", ".join([r.path for r in project_repos])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated module '{module.name}': set {num_linked} issues "
                    f"from repos: [{repo_names}]"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed. {total_links_created} issue links set across "
                f"{total_modules_updated} modules."
            )
        )
