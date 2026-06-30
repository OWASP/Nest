"""DataLoaders for projects."""

from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_m2m_results_by_keys
from apps.owasp.models.project import Project

PROJECT_BY_REPOSITORY_ID_LOADER = "project_by_repository_id"


async def load_projects_by_repository_id(
    repository_ids: list[int],
) -> list[Project | None]:
    """Batch-load the first project for the given repository IDs in a single query."""
    projects = (
        Project.objects.filter(repositories__in=repository_ids)
        .prefetch_related("repositories")
        .order_by("pk")
        .distinct()
    )

    results: list[list[Project | None]] = await get_m2m_results_by_keys(
        projects, repository_ids, m2m_field="repositories", key_field="pk"
    )

    return [result[0] if result else None for result in results]


def get_project_loaders() -> dict[str, DataLoader[int, Project | None]]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        PROJECT_BY_REPOSITORY_ID_LOADER: DataLoader[int, Project | None](
            load_fn=load_projects_by_repository_id,
        ),
    }
