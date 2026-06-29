"""DataLoaders for releases."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys, get_results_by_keys
from apps.github.models.release import Release

RECENT_RELEASES_LIMIT = 5
RELEASE_URL_BY_ID_LOADER = "release_url_by_id"
LATEST_RELEASE_BY_REPOSITORY_ID_LOADER = "latest_release_by_repository_id"
RECENT_RELEASES_BY_REPOSITORY_ID_LOADER = "recent_releases_by_repository_id"


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
    repository_ids: list[int],
) -> list[list[Release]]:
    """Batch-load recent releases for each repository ID."""
    recent_releases = Release.objects.filter(
        repository_id__in=repository_ids,
        is_draft=False,
        is_pre_release=False,
        published_at__isnull=False,
    ).order_by("repository_id", "-published_at")

    results: list[list[Release]] = await get_results_by_keys(
        recent_releases, repository_ids, key_field="repository_id"
    )

    return [group[:RECENT_RELEASES_LIMIT] for group in results]


def get_release_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        LATEST_RELEASE_BY_REPOSITORY_ID_LOADER: DataLoader[int, Release | None](
            load_fn=load_latest_releases_by_repository_id,
        ),
        RECENT_RELEASES_BY_REPOSITORY_ID_LOADER: DataLoader[int, list[Release]](
            load_fn=load_recent_releases_by_repository_id,
        ),
        RELEASE_URL_BY_ID_LOADER: DataLoader[int, str](
            load_fn=load_release_urls_by_id,
        ),
    }
