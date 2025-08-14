"""Syncs comments for issues relevant to active mentorship programs."""

import logging
import re

from django.core.management.base import BaseCommand
from github.GithubException import GithubException

from apps.github.auth import get_github_client
from apps.github.common import sync_issue_comments
from apps.github.models.issue import Issue
from apps.mentorship.models import ParticipantInterest, Program

logger = logging.getLogger(__name__)

INTEREST_PATTERNS = [
    r"assign.*me",
    r"i(?:'d| would)? like to work on",
    r"can i work on",
    r"i(?:'ll| will)? take",
    r"i want to work on",
    r"i am interested",
    r"can i be assigned",
    r"please assign.*me",
    r"i can (?:help|work|fix|handle)",
    r"let me (?:work|take|handle)",
    r"i(?:'ll| will).*(?:fix|handle|work)",
    r"assign.*to.*me",
    r"i volunteer",
    r"count me in",
    r"i(?:'m| am) up for",
    r"i could work",
    r"happy.*work",
    r"i(?:'d| would) love to work",
]


class Command(BaseCommand):
    """Syncs comments for issues relevant to active mentorship programs."""

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting mentorship issue processing job..."))

        gh = get_github_client()
        active_programs = Program.objects.filter(status=Program.ProgramStatus.PUBLISHED)
        if not active_programs.exists():
            self.stdout.write(self.style.WARNING("No active mentorship programs found. Exiting."))
            return

        for program in active_programs:
            self.stdout.write(f"\nProcessing program: {program.name}...")

            try:
                program_repos = (
                    program.modules.filter(project__repositories__isnull=False)
                    .values_list("project__repositories", flat=True)
                    .distinct()
                )
                self.stdout.write(
                    f"Program '{program.name}' have {program_repos.count()} repositories."
                )

                if not program_repos.exists():
                    self.stdout.write(
                        self.style.WARNING(f"Skipping. {program.name} has no repositories.")
                    )
                    continue

                relevant_issues = Issue.objects.filter(
                    repository_id__in=program_repos, state="open"
                ).distinct()

                self.stdout.write(f"Found {relevant_issues.count()} open issues across ")

            except GithubException as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping. Error querying GitHub data for program '{program.name}'. {e}"
                    )
                )
                continue

            for issue in relevant_issues:
                self.stdout.write(
                    f"Syncing new comments for issue #{issue.number} '{issue.title[:20]}...'"
                )
                sync_issue_comments(gh, issue)

                self._find_and_register_interest(issue, program)

        self.stdout.write(self.style.SUCCESS("\n processed successfully!"))

    def _find_and_register_interest(self, issue: Issue, program: Program):
        """Find and register users who expressed interest in given issue as part of program."""
        interest_obj, _ = ParticipantInterest.objects.get_or_create(program=program, issue=issue)

        new_users = []

        for comment in issue.comments.select_related("author").all():
            if not comment.author:
                continue

            if interest_obj.users.filter(id=comment.author.id).exists():
                continue

            body = (comment.body or "").lower()
            if any(re.search(pattern, body) for pattern in INTEREST_PATTERNS):
                interest_obj.users.add(comment.author)
                new_users.append(comment.author.login)

        if new_users:
            self.stdout.write(
                self.style.SUCCESS(
                    f"+ Added {len(new_users)} new user(s) "
                    f"to issue #{issue.number}: {', '.join(new_users)}"
                )
            )
