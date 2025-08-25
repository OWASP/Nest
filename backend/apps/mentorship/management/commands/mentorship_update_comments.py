"""Syncs comments for issues relevant to active mentorship modules."""

import logging
import re

from django.core.management.base import BaseCommand
from github.GithubException import GithubException

from apps.github.auth import get_github_client
from apps.github.common import sync_issue_comments
from apps.github.models.issue import Issue
from apps.mentorship.models import IssueUserInterest, Module, Program

logger = logging.getLogger(__name__)

INTEREST_PATTERNS = [
    re.compile(r"interested", re.IGNORECASE),
]


class Command(BaseCommand):
    """Syncs comments for issues relevant to active mentorship modules."""

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting mentorship issue processing job..."))

        gh = get_github_client()

        active_modules = Module.objects.filter(program__status=Program.ProgramStatus.PUBLISHED)
        if not active_modules.exists():
            self.stdout.write(self.style.WARNING("No active mentorship modules found. Exiting."))
            return

        for module in active_modules:
            self.stdout.write(f"\nProcessing module: {module.name}...")

            try:
                module_repos = (
                    module.project.repositories.filter(id__isnull=False)
                    .values_list("id", flat=True)
                    .distinct()
                )

                if not module_repos.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipping. Module '{module.name}' has no repositories."
                        )
                    )
                    continue

                relevant_issues = Issue.objects.filter(
                    repository_id__in=module_repos, state="open"
                ).distinct()

                self.stdout.write(
                    f"Found {relevant_issues.count()} open issues across repositories"
                )

            except GithubException as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping. Error querying GitHub data for module '{module.name}'. {e}"
                    )
                )
                continue

            for issue in relevant_issues:
                self.stdout.write(
                    f"Syncing new comments for issue #{issue.number} '{issue.title[:20]}...'"
                )
                sync_issue_comments(gh, issue)
                self._find_and_register_interest(issue, module)

        self.stdout.write(self.style.SUCCESS("\nProcessed successfully!"))

    def _find_and_register_interest(self, issue: Issue, module: Module):
        """Find and register contributors who expressed interest in a given issue."""
        existing_user_ids = set(
            IssueUserInterest.objects.filter(module=module, issue=issue).values_list(
                "user_id", flat=True
            )
        )

        interests_to_create = []
        new_user_logins = []

        for comment in issue.comments.select_related("author").all():
            if not comment.author or comment.author.id in existing_user_ids:
                continue

            body = comment.body or ""
            if any(p.search(body) for p in INTEREST_PATTERNS):
                interests_to_create.append(
                    IssueUserInterest(module=module, issue=issue, user=comment.author)
                )

                new_user_logins.append(comment.author.login)
                existing_user_ids.add(comment.author.id)

        if interests_to_create:
            IssueUserInterest.objects.bulk_create(interests_to_create)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Registered {len(interests_to_create)} new interest(s) "
                    f"for issue #{issue.number}: {', '.join(new_user_logins)}"
                )
            )
