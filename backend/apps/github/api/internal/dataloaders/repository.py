"""DataLoaders for repositories."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys
from apps.github.models.release import Release
from apps.github.models.repository import Repository

REPOSITORY_BY_RELEASE_ID_LOADER = "repository_by_release_id"


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


def get_repository_loaders() -> dict[str, DataLoader[int, Repository | None]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        REPOSITORY_BY_RELEASE_ID_LOADER: DataLoader[int, Repository | None](
            load_fn=load_repositories_by_release_id,
        ),
    }
