"""DataLoaders for repository contributors."""

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db.models import F, OuterRef, QuerySet, Subquery, Sum, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_top_contributors_by_keys
from apps.github.models.repository_contributor import RepositoryContributor
from apps.owasp.models.chapter import Chapter

TOP_CONTRIBUTORS_LIMIT = 15
TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER = "top_contributors_by_repository_id"
TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER = "top_contributors_by_project_id"
TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER = "top_contributors_by_chapter_id"

if TYPE_CHECKING:
    from apps.github.models.managers.repository_contributor import (
        RepositoryContributorQuerySet,
    )


async def load_top_contributors_by_repository_id(
    repository_ids: list[int],
) -> list[list[dict[str, str | int]]]:
    """Batch-load top contributors per repository (humans only, community repos).

    Capped at ``TOP_CONTRIBUTORS_LIMIT`` per repository.
    """
    if not repository_ids:
        return []

    queryset: RepositoryContributorQuerySet = await sync_to_async(
        lambda: RepositoryContributor.objects.by_humans().to_community_repositories()
    )()

    top_contributors: QuerySet[RepositoryContributor, dict[str, str | int]] = (
        queryset.filter(repository_id__in=repository_ids)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("repository_id")],
                order_by=F("contributions_count").desc(),
            ),
        )
        .filter(row_number__lte=TOP_CONTRIBUTORS_LIMIT)
        .values(
            "repository_id",
            "contributions_count",
            avatar_url=F("user__avatar_url"),
            login=F("user__login"),
            name=F("user__name"),
        )
        .order_by("repository_id", "-contributions_count")
    )

    return await get_top_contributors_by_keys(
        queryset=top_contributors, keys=repository_ids, key_field="repository_id"
    )


async def load_top_contributors_by_project_id(
    project_ids: list[int],
) -> list[list[dict[str, str | int]]]:
    """Batch-load top contributors per project (humans only, community repos).

    A single user's ``contributions_count`` is summed across every repository
    linked to a project via ``annotate(Sum(...))``, and the result is capped at
    ``TOP_CONTRIBUTORS_LIMIT`` per project.
    """
    if not project_ids:
        return []

    queryset: RepositoryContributorQuerySet = await sync_to_async(
        lambda: RepositoryContributor.objects.by_humans().to_community_repositories()
    )()

    top_contributors: QuerySet[RepositoryContributor, dict[str, str | int]] = (
        queryset.filter(repository__project__in=project_ids)
        .values(
            avatar_url=F("user__avatar_url"),
            login=F("user__login"),
            name=F("user__name"),
            project_id=F("repository__project__id"),
        )
        .annotate(contributions_count=Sum("contributions_count"))
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("project_id")],
                order_by=F("contributions_count").desc(),
            ),
        )
        .filter(row_number__lte=TOP_CONTRIBUTORS_LIMIT)
        .order_by("project_id", "-contributions_count")
    )
    return await get_top_contributors_by_keys(
        queryset=top_contributors,
        keys=project_ids,
        key_field="project_id",
    )


async def load_top_contributors_by_chapter_id(
    chapter_ids: list[int],
) -> list[list[dict[str, str | int]]]:
    """Batch-load top contributors per chapter (humans only, community repos).

    A chapter's top contributors are the top contributors of its main OWASP
    repository (``owasp_repository``). Results are capped at
    ``TOP_CONTRIBUTORS_LIMIT`` per chapter.
    """
    if not chapter_ids:
        return []

    queryset: RepositoryContributorQuerySet = await sync_to_async(
        lambda: RepositoryContributor.objects.by_humans().to_community_repositories()
    )()

    top_contributors: QuerySet[RepositoryContributor, dict[str, str | int]] = (
        queryset.filter(
            repository_id__in=Chapter.objects.filter(id__in=chapter_ids).values(
                "owasp_repository_id"
            )
        )
        .annotate(
            chapter_id=Subquery(
                Chapter.objects.filter(
                    id__in=chapter_ids,
                    owasp_repository_id=OuterRef("repository_id"),
                ).values("id")[:1]
            ),
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("chapter_id")],
                order_by=F("contributions_count").desc(),
            ),
        )
        .filter(row_number__lte=TOP_CONTRIBUTORS_LIMIT)
        .values(
            "chapter_id",
            "contributions_count",
            avatar_url=F("user__avatar_url"),
            login=F("user__login"),
            name=F("user__name"),
        )
        .order_by("chapter_id", "-contributions_count")
    )

    return await get_top_contributors_by_keys(
        queryset=top_contributors,
        keys=chapter_ids,
        key_field="chapter_id",
    )


def get_repository_contributor_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        TOP_CONTRIBUTORS_BY_CHAPTER_ID_LOADER: DataLoader[int, list[dict[str, str | int]]](
            load_fn=load_top_contributors_by_chapter_id
        ),
        TOP_CONTRIBUTORS_BY_PROJECT_ID_LOADER: DataLoader[int, list[dict[str, str | int]]](
            load_fn=load_top_contributors_by_project_id
        ),
        TOP_CONTRIBUTORS_BY_REPOSITORY_ID_LOADER: DataLoader[int, list[dict[str, str | int]]](
            load_fn=load_top_contributors_by_repository_id
        ),
    }
