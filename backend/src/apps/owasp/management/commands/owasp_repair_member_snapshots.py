"""Repair GitHub activity in explicitly selected existing member snapshots."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.owasp.management.commands.owasp_create_member_snapshot import Command as SnapshotCommand
from apps.owasp.models.member_snapshot import MemberSnapshot


class Command(BaseCommand):
    """Preserve snapshot identity, reporting dates and Slack communication data."""

    help = "Rebuild GitHub fields of existing snapshots from locally stored contributions"

    def add_arguments(self, parser):
        """Require explicit snapshot IDs; never choose historical periods implicitly."""
        parser.add_argument("snapshot_ids", nargs="+", type=int)

    def handle(self, *args, **options):
        """Lock each snapshot and replace its GitHub fields atomically."""
        generator = SnapshotCommand()
        with transaction.atomic():
            for snapshot_id in dict.fromkeys(options["snapshot_ids"]):
                snapshot = (
                    MemberSnapshot.objects.select_for_update().filter(pk=snapshot_id).first()
                )
                if snapshot is None or snapshot.github_user_id is None:
                    message = f"Snapshot {snapshot_id} does not exist or has no GitHub user"
                    raise CommandError(message)
                start, end = snapshot.start_at, snapshot.end_at
                user = snapshot.github_user
                commits, pulls, issues = (
                    model.objects.filter(author=user, created_at__gte=start, created_at__lte=end)
                    for model in (Commit, PullRequest, Issue)
                )
                snapshot.commits.set(commits)
                snapshot.pull_requests.set(pulls)
                snapshot.issues.set(issues)
                snapshot.contribution_heatmap_data = generator.generate_heatmap_data(
                    commits, pulls, issues, start, end
                )
                for entity_type in ("chapter", "project"):
                    setattr(
                        snapshot,
                        f"{entity_type}_contributions",
                        generator.generate_entity_contributions(
                            user,
                            commits,
                            pulls,
                            issues,
                            entity_type=entity_type,
                            start_at=start,
                            end_at=end,
                        ),
                    )
                snapshot.repository_contributions = generator.generate_repository_contributions(
                    commits, start, end
                )
                snapshot.save(
                    update_fields=[
                        "contribution_heatmap_data",
                        "chapter_contributions",
                        "project_contributions",
                        "repository_contributions",
                    ]
                )
                self.stdout.write(f"Repaired GitHub activity for snapshot {snapshot.pk}")
