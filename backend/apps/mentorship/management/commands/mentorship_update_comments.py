"""Syncs comments for issues relevant to active mentorship modules."""

import logging
import re

from django.core.management.base import BaseCommand

from apps.github.auth import get_github_client
from apps.github.common import sync_issue_comments
from apps.github.models.issue import Issue
from apps.mentorship.models import IssueUserInterest, Module, Program

logger = logging.getLogger(__name__)

INTEREST_PATTERNS = [
    re.compile(r"/interested", re.IGNORECASE),
]


class Command(BaseCommand):
    """Syncs comments for issues relevant to active mentorship modules."""

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting mentorship issue processing job..."))

        active_modules = Module.objects.filter(program__status=Program.ProgramStatus.PUBLISHED)
        if not active_modules.exists():
            self.stdout.write(self.style.WARNING("No active mentorship modules found. Exiting."))
            return

        for module in active_modules:
            self.stdout.write(f"\nProcessing module: {module.name}...")

            gh = get_github_client()

            module_repos = (
                module.project.repositories.filter(id__isnull=False)
                .values_list("id", flat=True)
                .distinct()
            )

            if not module_repos.exists():
                self.stdout.write(
                    self.style.WARNING(f"Skipping. Module '{module.name}' has no repositories.")
                )
                continue

            relevant_issues = Issue.objects.filter(
                repository_id__in=module_repos, state="open"
            ).distinct()

            self.stdout.write(f"Found {relevant_issues.count()} open issues across repositories")

            for issue in relevant_issues:
                self.stdout.write(
                    f"Syncing new comments for issue #{issue.number} '{issue.title[:20]}...'"
                )
                sync_issue_comments(gh, issue)
                self._find_and_register_interest(issue, module)

        self.stdout.write(self.style.SUCCESS("\nProcessed successfully!"))

    def _find_and_register_interest(self, issue: Issue, module: Module):
        """Find and register contributors who expressed interest in a given issue."""
        existing_interests = IssueUserInterest.objects.filter(module=module, issue=issue)
        existing_user_ids = set(existing_interests.values_list("user_id", flat=True))

        last_sync = getattr(issue, "last_comment_sync", None)

        if last_sync:
            comments_to_process = (
                issue.comments.filter(updated_at__gt=last_sync)
                .select_related("author")
                .order_by("created_at")
            )
        else:
            comments_to_process = issue.comments.select_related("author").order_by("created_at")

        interests_to_create = []
        new_user_logins = []

        for comment in comments_to_process:
            if not comment.author:
                continue

            body = comment.body or ""
            user_id = comment.author.id

            is_interested = any(p.search(body) for p in INTEREST_PATTERNS)

            if is_interested and user_id not in existing_user_ids:
                interests_to_create.append(
                    IssueUserInterest(module=module, issue=issue, user=comment.author)
                )
                new_user_logins.append(comment.author.login)
                existing_user_ids.add(user_id)

        if interests_to_create:
            IssueUserInterest.objects.bulk_create(interests_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Registered {len(interests_to_create)} new interest(s) "
                    f"for issue #{issue.number}: {', '.join(new_user_logins)}"
                )
            )
