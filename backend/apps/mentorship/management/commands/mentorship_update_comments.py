"""Syncs comments for issues relevant to active mentorship modules."""

import logging
import re

from django.core.management.base import BaseCommand

from apps.github.auth import get_github_client
from apps.github.common import sync_issue_comments
from apps.github.models.issue import Issue
from apps.mentorship.models import IssueUserInterest, Module, Program

logger: logging.Logger = logging.getLogger(__name__)

INTEREST_PATTERNS = [
    re.compile(r"/interested", re.IGNORECASE),
]


class Command(BaseCommand):
    """Sync comments for issues relevant to active mentorship modules and process interests."""

    help = "Sync comments for issues relevant to active mentorship modules and process interests"

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        try:
            self.process_mentorship_modules()
        except Exception as e:
            error_msg = f"Failed to process mentorship modules: {e}"
            logger.exception(error_msg)
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def process_mentorship_modules(self) -> None:
        """Process all active mentorship modules."""
        active_modules = Module.objects.filter(program__status=Program.ProgramStatus.PUBLISHED)

        if not active_modules.exists():
            self.stdout.write(self.style.WARNING("No active mentorship modules found. Exiting."))
            return

        self.stdout.write(self.style.SUCCESS("Starting mentorship issue processing job..."))

        for module in active_modules:
            self.stdout.write(f"\nProcessing module: {module.name}...")
            self.process_module(module)

        self.stdout.write(self.style.SUCCESS("\nProcessed successfully!"))

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
            repository_id__in=module_repos, state="open"
        ).distinct()

        self.stdout.write(f"Found {relevant_issues.count()} open issues across repositories")

        for issue in relevant_issues:
            self.stdout.write(
                f"Syncing comments for issue #{issue.number} '{issue.title[:20]}...'"
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

        all_comments = issue.comments.select_related("author").order_by("author_id", "-created_at")

        interests_to_create = []
        interests_to_remove = []
        new_user_logins = []
        removed_user_logins = []

        user_interest_status = {}
        processed_users = set()

        for comment in all_comments:
            if not comment.author or comment.author.id in processed_users:
                continue

            body = comment.body or ""
            user_id = comment.author.id
            user_login = comment.author.login

            is_interested = any(pattern.search(body) for pattern in INTEREST_PATTERNS)

            user_interest_status[user_id] = {
                "is_interested": is_interested,
                "login": user_login,
                "author": comment.author,
            }
            processed_users.add(user_id)

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
