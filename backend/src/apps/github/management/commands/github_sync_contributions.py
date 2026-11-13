"""Repair dated contribution history for selected linked repositories."""

from datetime import UTC, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.utils.index import disable_indexing
from apps.github.auth import get_github_client
from apps.github.common import (
    get_contribution_repositories,
    sync_repository_commits,
    sync_repository_issues,
    sync_repository_pull_requests,
)
from apps.owasp.management.commands.owasp_aggregate_entity_contributions import (
    Command as AggregateCommand,
)
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


class Command(BaseCommand):
    """Run bounded, repeatable contribution backfills without metadata synchronization."""

    help = "Backfill contributions for repositories linked to active projects or chapters"

    def add_arguments(self, parser):
        """Require an explicit selection and bound each invocation."""
        selection = parser.add_mutually_exclusive_group(required=True)
        selection.add_argument("--repository", help="Repository path, e.g. OWASP/Nest")
        selection.add_argument("--organization", help="Repository owner login")
        selection.add_argument("--all", action="store_true", dest="all_repositories")
        period = parser.add_mutually_exclusive_group()
        period.add_argument("--days", type=int, default=None)
        period.add_argument("--since", help="Timezone-aware ISO 8601 start time")
        parser.add_argument(
            "--types",
            nargs="+",
            choices=["commits", "issues", "pull_requests"],
            default=["commits", "issues", "pull_requests"],
        )
        parser.add_argument("--force", action="store_true")
        parser.add_argument(
            "--refresh",
            action="store_true",
            help="Refresh affected project/chapter activity after successful imports",
        )
        parser.add_argument("--offset", type=int, default=0)
        parser.add_argument("--limit", type=int, default=25)

    def handle(self, *args, **options):
        """Continue independent imports, but return failure if any import is incomplete."""
        if options["offset"] < 0 or options["limit"] <= 0:
            msg = "Offset must be nonnegative and limit must be positive"
            raise CommandError(msg)
        end_at = timezone.now().astimezone(UTC)
        if options["since"]:
            try:
                start_at = datetime.fromisoformat(options["since"])
            except ValueError as error:
                msg = "Since must be a timezone-aware ISO 8601 timestamp"
                raise CommandError(msg) from error
            if timezone.is_naive(start_at):
                msg = "Since must include a timezone"
                raise CommandError(msg)
            start_at = start_at.astimezone(UTC)
        else:
            days = options["days"] if options["days"] is not None else 365
            if days <= 0:
                msg = "Days must be positive"
                raise CommandError(msg)
            try:
                start_at = end_at - timedelta(days=days)
            except OverflowError as error:
                msg = "Days exceeds the supported date range"
                raise CommandError(msg) from error
        if start_at > end_at:
            msg = "Since must not be in the future"
            raise CommandError(msg)
        repositories = get_contribution_repositories().select_related("owner").order_by("pk")
        if path := options["repository"]:
            parts = path.partition("/")
            if not all(parts) or "/" in parts[2]:
                msg = "Repository must be an owner/name path"
                raise CommandError(msg)
            repositories = repositories.filter(
                owner__login__iexact=parts[0], name__iexact=parts[2]
            )
        elif owner := options["organization"]:
            repositories = repositories.filter(owner__login__iexact=owner)
        repositories = list(repositories[options["offset"] : options["offset"] + options["limit"]])
        if not repositories:
            msg = "No eligible repositories matched the selection"
            raise CommandError(msg)
        collectors = {
            "commits": sync_repository_commits,
            "issues": sync_repository_issues,
            "pull_requests": sync_repository_pull_requests,
        }
        failures = 0
        client = get_github_client()
        try:
            with disable_indexing():
                for repository in repositories:
                    try:
                        remote = client.get_repo(repository.path)
                        if remote.node_id != repository.node_id:
                            msg = "Repository identity changed"
                            raise ValueError(msg)  # noqa: TRY301 - report this repository and continue
                    except Exception as error:  # noqa: BLE001 - report incomplete imports and continue
                        failures += 1
                        self.stderr.write(
                            f"Repository {repository.pk}: fetch failed ({type(error).__name__})"
                        )
                        continue
                    for kind in dict.fromkeys(options["types"]):
                        if kind == "issues" and (
                            not repository.track_issues
                            or (repository.project and not repository.project.track_issues)
                        ):
                            self.stdout.write(
                                f"{repository.path}: issues skipped (tracking disabled)"
                            )
                            continue
                        try:
                            collectors[kind](
                                remote,
                                repository,
                                start_at=start_at,
                                end_at=end_at,
                                force=options["force"],
                            )
                        except Exception as error:  # noqa: BLE001 - report incomplete imports and continue
                            failures += 1
                            self.stderr.write(
                                f"{repository.path}: {kind} failed ({type(error).__name__})"
                            )
                        else:
                            self.stdout.write(f"{repository.path}: {kind} completed")
        finally:
            client.close()
        if failures:
            msg = f"Contribution synchronization incomplete: {failures} failures"
            raise CommandError(msg)

        if options.get("refresh"):
            self.refresh_activity(repositories, start_at, end_at)

    def refresh_activity(self, repositories, start_at, end_at):
        """Regenerate affected entities for the exact imported period, atomically."""
        repository_ids = [repository.pk for repository in repositories]
        projects = Project.active_projects.filter(
            Q(owasp_repository_id__in=repository_ids) | Q(repositories__pk__in=repository_ids)
        ).distinct()
        chapters = Chapter.active_chapters.filter(owasp_repository_id__in=repository_ids)
        aggregator = AggregateCommand()
        with disable_indexing(), transaction.atomic():
            for entities in (projects, chapters):
                for entity in entities:
                    data, stats = aggregator.aggregate_contributions(entity, start_at, end_at)
                    type(entity).objects.filter(pk=entity.pk).update(
                        contribution_data=data, contribution_stats=stats
                    )
        self.stdout.write(
            "Affected project and chapter activity recalculated from stored data. "
            "Only selected repositories were synchronized; other linked repositories "
            "may still have incomplete history."
        )
