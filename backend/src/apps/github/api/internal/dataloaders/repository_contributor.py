"""DataLoaders for repository contributors."""

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_top_contributors_by_keys
from apps.github.models.repository_contributor import RepositoryContributor

TOP_CONTRIBUTORS_LIMIT = 15
TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER = "top_contributors_by_repository_id"

if TYPE_CHECKING:
    from apps.github.models.managers.repository_contributor import (
        RepositoryContributorQuerySet,
    )


async def load_top_contributors_by_repository_id(
    repository_ids: list[int],
) -> list[list[dict[str, str | int]]]:
    """Batch-load top contributors for the given repository IDs in a single query.

    Mirrors the per-repository slice of RepositoryContributor.get_top_contributors
    (humans only, community repositories), ranked by contributions and capped at
    TOP_CONTRIBUTORS_LIMIT per repository.

    ``RepositoryContributor`` has ``unique_together = ("repository", "user")``, so each
    user has exactly one row per repository and ``contributions_count`` is already the
    user's total for that repository. Ranking by ``contributions_count`` therefore
    matches the original aggregate (``Sum``+``GROUP BY``) without a window-on-aggregate
    query, which Postgres forbids.
    """
    if not repository_ids:
        return []

    queryset: RepositoryContributorQuerySet = await sync_to_async(
        lambda: RepositoryContributor.objects.by_humans().to_community_repositories()
    )()

    top_contributors: RepositoryContributorQuerySet = (
        queryset.filter(repository_id__in=repository_ids)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("repository_id")],
                order_by=F("contributions_count").desc(),
            ),
        )
        .filter(row_number__lte=TOP_CONTRIBUTORS_LIMIT)
        .order_by("repository_id", "-contributions_count")
    )

    return await get_top_contributors_by_keys(
        queryset=top_contributors, keys=repository_ids, key_field="repository_id"
    )


def get_repository_contributor_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER: DataLoader[int, list[dict[str, str | int]]](
            load_fn=load_top_contributors_by_repository_id
        ),
    }
