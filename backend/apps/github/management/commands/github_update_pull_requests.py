"""Link pull requests to issues via closing keywords in PR body (e.g., 'closes #123')."""

import logging
import re

from django.core.management.base import BaseCommand

from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Link pull requests to issues via closing keywords in PR body (e.g., 'closes #123')."

    # regex pattern to find the linked issue
    pattern = re.compile(
        r"\b(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\b\s+"
        r"#(\d+)",
        re.IGNORECASE,
    )

    def handle(self, *args, **options):
        linked = 0
        updated_prs = []

        logger.info("Linking PRs to issues using closing keywords")

        queryset = PullRequest.objects.select_related("repository").all()

        for pr in queryset:
            if not pr.repository:
                logger.info("Skipping PR #%s: no repository", pr.number)
                continue

            body = pr.body or ""
            matches = self.pattern.findall(body)
            if not matches:
                logger.info("No closing keyword pattern found for PR #%s", pr.number)
                continue
            issue_numbers = {int(n) for n in matches}

            issues = list(Issue.objects.filter(repository=pr.repository, number__in=issue_numbers))

            existing_ids = set(pr.related_issues.values_list("id", flat=True))
            new_ids = {i.id for i in issues} - existing_ids
            if new_ids:
                pr.related_issues.add(*new_ids)
                linked += len(new_ids)
                updated_prs.append(pr)
                self.stdout.write(
                    f"Linked PR #{pr.number} ({pr.repository.name}) -> Issues "
                    + ", ".join(f"#{i.number}" for i in issues if i.id in new_ids)
                )

        if updated_prs:
            PullRequest.bulk_save(updated_prs)

        self.stdout.write(f"Linked: {linked}")
