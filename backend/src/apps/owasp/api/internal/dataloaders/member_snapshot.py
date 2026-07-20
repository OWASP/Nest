"""DataLoaders for member snapshots."""

from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_values_by_keys
from apps.owasp.models.member_snapshot import MemberSnapshot

COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER = "commits_count_by_snapshot_id"
ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER = "issues_count_by_snapshot_id"
MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER = "messages_count_by_snapshot_id"
PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER = "pull_requests_count_by_snapshot_id"
TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER = "total_contributions_by_snapshot_id"


async def load_count_by_snapshot_id(snapshot_ids: list[int], field: str) -> list[int]:
    """Batch-load a related M2M count for the given member snapshot IDs."""
    snapshots = (
        MemberSnapshot.objects.filter(pk__in=snapshot_ids)
        .annotate(count=Count(field, distinct=True))
        .values_list("pk", "count")
    )
    return await get_values_by_keys(snapshots, snapshot_ids, default=0)


async def load_commits_count_by_snapshot_id(snapshot_ids: list[int]) -> list[int]:
    """Batch-load commits count for the given member snapshot IDs."""
    return await load_count_by_snapshot_id(snapshot_ids, "commits")


async def load_issues_count_by_snapshot_id(snapshot_ids: list[int]) -> list[int]:
    """Batch-load issues count for the given member snapshot IDs."""
    return await load_count_by_snapshot_id(snapshot_ids, "issues")


async def load_messages_count_by_snapshot_id(snapshot_ids: list[int]) -> list[int]:
    """Batch-load Slack messages count for the given member snapshot IDs."""
    return await load_count_by_snapshot_id(snapshot_ids, "messages")


async def load_pull_requests_count_by_snapshot_id(snapshot_ids: list[int]) -> list[int]:
    """Batch-load pull requests count for the given member snapshot IDs."""
    return await load_count_by_snapshot_id(snapshot_ids, "pull_requests")


async def load_total_contributions_by_snapshot_id(snapshot_ids: list[int]) -> list[int]:
    """Batch-load total contributions for the given member snapshot IDs."""
    snapshots = (
        MemberSnapshot.objects.filter(pk__in=snapshot_ids)
        .annotate(
            total=Coalesce(
                Subquery(
                    MemberSnapshot.objects.filter(pk=OuterRef("pk"))
                    .values("pk")
                    .annotate(count=Count("commits"))
                    .values("count"),
                    output_field=IntegerField(),
                ),
                0,
            )
            + Coalesce(
                Subquery(
                    MemberSnapshot.objects.filter(pk=OuterRef("pk"))
                    .values("pk")
                    .annotate(count=Count("pull_requests"))
                    .values("count"),
                    output_field=IntegerField(),
                ),
                0,
            )
            + Coalesce(
                Subquery(
                    MemberSnapshot.objects.filter(pk=OuterRef("pk"))
                    .values("pk")
                    .annotate(count=Count("issues"))
                    .values("count"),
                    output_field=IntegerField(),
                ),
                0,
            ),
        )
        .values_list("pk", "total")
    )
    return await get_values_by_keys(snapshots, snapshot_ids, default=0)


def get_member_snapshot_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        COMMITS_COUNT_BY_SNAPSHOT_ID_LOADER: DataLoader[int, int](
            load_fn=load_commits_count_by_snapshot_id,
        ),
        ISSUES_COUNT_BY_SNAPSHOT_ID_LOADER: DataLoader[int, int](
            load_fn=load_issues_count_by_snapshot_id,
        ),
        MESSAGES_COUNT_BY_SNAPSHOT_ID_LOADER: DataLoader[int, int](
            load_fn=load_messages_count_by_snapshot_id,
        ),
        PULL_REQUESTS_COUNT_BY_SNAPSHOT_ID_LOADER: DataLoader[int, int](
            load_fn=load_pull_requests_count_by_snapshot_id,
        ),
        TOTAL_CONTRIBUTIONS_BY_SNAPSHOT_ID_LOADER: DataLoader[int, int](
            load_fn=load_total_contributions_by_snapshot_id,
        ),
    }
