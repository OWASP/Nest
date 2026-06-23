"""DataLoaders for repositories."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_first_by_m2m_keys, get_result_by_keys
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.owasp.constants import OWASP_ORGANIZATION_NAME
from apps.owasp.models.project import Project

REPOSITORY_BY_RELEASE_ID_LOADER = "repository_by_release_id"
REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER = "repository_project_name_by_release_id"


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


async def load_repository_project_names_by_release_id(
    release_ids: list[int],
) -> list[str | None]:
    """Batch-load repository project names for the given release IDs."""
    releases = Release.objects.filter(pk__in=release_ids).only("pk", "repository_id")

    release_repo_map: dict[int, int | None] = {}
    repo_ids: set[int] = set()
    async for release in releases:
        release_repo_map[release.pk] = release.repository_id
        if release.repository_id is not None:
            repo_ids.add(release.repository_id)

    project_name_by_repo = (
        await get_first_by_m2m_keys(
            Project,
            "repositories",
            repo_ids,
            target_fk_field="repository_id",
            source_select_related="project",
            value_field="name",
        )
        if repo_ids
        else {}
    )
    project_name_by_repo = {
        repo_id: name.removeprefix(f"{OWASP_ORGANIZATION_NAME} ") if name else None
        for repo_id, name in project_name_by_repo.items()
    }

    result: list[str | None] = []
    for release_id in release_ids:
        repo_id = release_repo_map.get(release_id)
        result.append(project_name_by_repo.get(repo_id) if repo_id is not None else None)

    return result


def get_repository_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        REPOSITORY_BY_RELEASE_ID_LOADER: DataLoader[int, Repository | None](
            load_fn=load_repositories_by_release_id,
        ),
        REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER: DataLoader[int, str | None](
            load_fn=load_repository_project_names_by_release_id,
        ),
    }
