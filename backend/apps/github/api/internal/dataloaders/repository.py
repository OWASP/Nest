"""DataLoaders for repositories."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys
from apps.github.models.release import Release
from apps.github.models.repository import Repository

REPOSITORY_BY_RELEASE_ID_LOADER = "repository_by_release_id"
RELEASE_URL_BY_ID_LOADER = "release_url_by_id"


async def load_repositories_by_release_id(
    release_ids: list[int],
) -> list[Repository | None]:
    """Batch-load repositories for the given release IDs in a single query."""
    releases = Release.objects.filter(pk__in=release_ids).select_related(
        "repository__organization", "repository__owner"
    )

    return await get_result_by_keys(
        releases, release_ids, key_field="pk", value_field="repository"
    )


async def load_release_urls_by_id(release_ids: list[int]) -> list[str]:
    """Batch-load release URLs for the given release IDs in a single query."""
    releases = Release.objects.filter(pk__in=release_ids).select_related(
        "repository__owner", "repository__organization"
    )

    mapping: dict[int, str] = {}
    async for release in releases:
        if release.repository:
            mapping[release.pk] = f"{release.repository.url}/releases/tag/{release.tag_name}"
        else:
            mapping[release.pk] = ""

    return [mapping.get(release_id, "") for release_id in release_ids]


def get_repository_loaders() -> dict[
    str,
    DataLoader[int, Repository | None] | DataLoader[int, str],
]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        REPOSITORY_BY_RELEASE_ID_LOADER: DataLoader[int, Repository | None](
            load_fn=load_repositories_by_release_id,
        ),
        RELEASE_URL_BY_ID_LOADER: DataLoader[int, str](
            load_fn=load_release_urls_by_id,
        ),
    }
