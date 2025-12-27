"""Sync comments for issues relevant to published mentorship modules."""

import logging
import re
from typing import Any

from django.core.management.base import BaseCommand

from apps.common.utils import truncate
from apps.github.auth import get_github_client
from apps.github.common import sync_issue_comments
from apps.github.models.issue import Issue
from apps.mentorship.models import IssueUserInterest, Module

logger: logging.Logger = logging.getLogger(__name__)

INTEREST_PATTERNS = [
    re.compile(r"/interested", re.IGNORECASE),
]


class Command(BaseCommand):
    """Sync comments for issues relevant to active mentorship modules and process interests."""

    help = "Sync comments for issues relevant to active mentorship modules and process interests"

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        self.process_mentorship_modules()

    def process_mentorship_modules(self) -> None:
        """Process all active mentorship modules."""
        published_modules = Module.published_modules.all()

        if not published_modules.exists():
            self.stdout.write(
                self.style.WARNING("No published mentorship modules found. Exiting.")
            )
            return

        self.stdout.write(self.style.SUCCESS("Starting mentorship issue processing job..."))

        modules_with_labels = published_modules.exclude(labels=[]).select_related("project")

        if not modules_with_labels.exists():
            self.stdout.write(
                self.style.WARNING("No published mentorship modules with labels found. Exiting.")
            )
            return

        for module in modules_with_labels:
            self.stdout.write(f"\nProcessing module: {module.name}...")
            self.process_module(module)

        self.stdout.write(self.style.SUCCESS("Processed successfully!"))

    def process_module(self, module: Module) -> None:
        """Process a single mentorship module.

        Args:
            module (Module): The module instance to process.

        """
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
            return

        relevant_issues = Issue.objects.filter(
            repository_id__in=module_repos, state=Issue.State.OPEN
        ).distinct()

        self.stdout.write(f"Found {relevant_issues.count()} open issues across repositories")

        for issue in relevant_issues:
            self.stdout.write(
                f"Syncing comments for issue #{issue.number} '{truncate(issue.title, 20)}'"
            )
            sync_issue_comments(gh, issue)
            self.process_issue_interests(issue, module)

    def process_issue_interests(self, issue: Issue, module: Module) -> None:
        """Process interests for a single issue.

        Args:
            issue (Issue): The issue instance to process.
            module (Module): The module instance.

        """
        existing_interests = IssueUserInterest.objects.filter(module=module, issue=issue)
        existing_user_ids = set(existing_interests.values_list("user_id", flat=True))

        all_comments = (
            issue.comments.select_related("author")
            .filter(author__isnull=False)
            .order_by("author_id", "nest_created_at")
        )

        interests_to_create = []
        interests_to_remove = []
        new_user_logins = []
        removed_user_logins = []

        user_interest_status: dict[int, dict[str, Any]] = {}

        for comment in all_comments:
            user_id = comment.author.id
            entry = user_interest_status.get(user_id)
            is_match = any(p.search(comment.body or "") for p in INTEREST_PATTERNS)
            if entry:
                entry["is_interested"] = entry["is_interested"] or is_match
            else:
                user_interest_status[user_id] = {
                    "is_interested": is_match,
                    "login": comment.author.login,
                    "author": comment.author,
                }

        for user_id, status in user_interest_status.items():
            is_interested = status["is_interested"]
            user_login = status["login"]
            author = status["author"]

            if is_interested and user_id not in existing_user_ids:
                interests_to_create.append(
                    IssueUserInterest(module=module, issue=issue, user=author)
                )
                new_user_logins.append(user_login)
            elif not is_interested and user_id in existing_user_ids:
                interests_to_remove.append(user_id)
                removed_user_logins.append(user_login)

        if interests_to_create:
            IssueUserInterest.objects.bulk_create(interests_to_create)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Registered {len(interests_to_create)} new interest(s) "
                    f"for issue #{issue.number}: {', '.join(new_user_logins)}"
                )
            )

        if interests_to_remove:
            removed_count = IssueUserInterest.objects.filter(
                module=module, issue=issue, user_id__in=interests_to_remove
            ).delete()[0]
            self.stdout.write(
                self.style.WARNING(
                    f"Unregistered {removed_count} interest(s) "
                    f"for issue #{issue.number}: {', '.join(removed_user_logins)}"
                )
            )
