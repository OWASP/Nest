"""DataLoaders for releases."""

from strawberry.dataloader import DataLoader

from apps.github.models.release import Release

RELEASE_URL_BY_ID_LOADER = "release_url_by_id"


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


def get_release_loaders() -> dict[str, DataLoader[int, str]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        RELEASE_URL_BY_ID_LOADER: DataLoader[int, str](
            load_fn=load_release_urls_by_id,
        ),
    }
