"""DataLoaders for releases."""

from collections import defaultdict

from django.db.models import F, Prefetch, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys, get_results_by_keys
from apps.github.models.release import Release
from apps.owasp.models.project import Project

RECENT_RELEASES_LIMIT = 5
RELEASE_URL_BY_ID_LOADER = "release_url_by_id"
LATEST_RELEASE_BY_REPOSITORY_ID_LOADER = "latest_release_by_repository_id"
RECENT_RELEASES_BY_REPOSITORY_ID_LOADER = "recent_releases_by_repository_id"
RECENT_RELEASES_BY_PROJECT_ID = "recent_releases_by_project_id"


async def load_recent_releases_by_project_id(
    keys: list[tuple[int, int]],
) -> list[list[Release]]:
    """Batch-load recent published releases across the given projects' repositories."""
    if not keys:
        return []

    project_ids = [key[0] for key in keys]
    limit = keys[0][1]

    releases = (
        Release.objects.filter(
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
            repository__project__in=project_ids,
        )
        .prefetch_related(
            Prefetch(
                "repository__project_set",
                queryset=Project.objects.filter(pk__in=project_ids).only("pk"),
                to_attr="prefetched_projects",
            ),
        )
        .order_by("-published_at")
        .distinct()
    )

    mapping: dict[int, list[Release]] = defaultdict(list)
    async for release in releases:
        for project in release.repository.prefetched_projects:
            if len(mapping[project.pk]) < limit:
                mapping[project.pk].append(release)

    return [mapping.get(project_id, []) for project_id in project_ids]


async def load_release_urls_by_id(release_ids: list[int]) -> list[str]:
    """Batch-load release URLs for the given release IDs in a single query."""
    releases = Release.objects.filter(pk__in=release_ids).select_related("repository__owner")

    mapping: dict[int, str] = {}
    async for release in releases:
        mapping[release.pk] = (
            f"{release.repository.url}/releases/tag/{release.tag_name}"
            if release.repository
            else ""
        )

    return [mapping.get(release_id, "") for release_id in release_ids]


async def load_latest_releases_by_repository_id(
    repository_ids: list[int],
) -> list[Release | None]:
    """Batch-load the latest release for each repository ID."""
    latest_releases = (
        Release.objects.filter(
            repository_id__in=repository_ids,
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )
        .distinct("repository_id")
        .select_related("author")
        .order_by("repository_id", "-published_at")
        .only("repository_id", "author__login", "author__name", "name")
    )

    return await get_result_by_keys(latest_releases, repository_ids, key_field="repository_id")


async def load_recent_releases_by_repository_id(
    keys: list[tuple[int, int]],
) -> list[list[Release]]:
    """Batch-load recent releases for each repository ID."""
    if not keys:
        return []

    repository_ids = [key[0] for key in keys]
    limit = keys[0][1]

    recent_releases = (
        Release.objects.filter(
            repository_id__in=repository_ids,
            is_draft=False,
            is_pre_release=False,
            published_at__isnull=False,
        )
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("repository_id")],
                order_by=F("published_at").desc(),
            )
        )
        .filter(row_number__lte=limit)
        .order_by("repository_id", "-published_at")
    )

    return await get_results_by_keys(recent_releases, repository_ids, key_field="repository_id")


def get_release_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        LATEST_RELEASE_BY_REPOSITORY_ID_LOADER: DataLoader[int, Release | None](
            load_fn=load_latest_releases_by_repository_id,
        ),
        RECENT_RELEASES_BY_REPOSITORY_ID_LOADER: DataLoader[tuple[int, int], list[Release]](
            load_fn=load_recent_releases_by_repository_id,
        ),
        RELEASE_URL_BY_ID_LOADER: DataLoader[int, str](
            load_fn=load_release_urls_by_id,
        ),
        RECENT_RELEASES_BY_PROJECT_ID: DataLoader[tuple[int, int], list[Release]](
            load_fn=load_recent_releases_by_project_id,
        ),
    }
