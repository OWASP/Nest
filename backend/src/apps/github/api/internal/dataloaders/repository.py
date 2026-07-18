"""DataLoaders for repositories."""

from collections import defaultdict

from django.db.models import Prefetch
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_result_by_keys
from apps.github.models.release import Release
from apps.github.models.repository import Repository
from apps.owasp.constants import OWASP_ORGANIZATION_NAME
from apps.owasp.models.project import Project

REPOSITORY_BY_RELEASE_ID_LOADER = "repository_by_release_id"
REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER = "repository_project_name_by_release_id"
REPOSITORIES_BY_PROJECT_ID = "repositories_by_project_id"


async def load_repositories_by_project_id(
    project_ids: list[int],
) -> list[list[Repository]]:
    """Batch-load repositories for the given project IDs in a single query.

    Repositories without an organization (filtered out by the M2M resolver) are
    excluded, mirroring the original ProjectNode resolver.
    """
    if not project_ids:
        return []

    repositories = (
        Repository.objects.filter(project__in=project_ids, organization__isnull=False)
        .select_related("organization")
        .prefetch_related(
            Prefetch(
                "project_set",
                queryset=Project.objects.filter(pk__in=project_ids).only("pk"),
                to_attr="prefetched_projects",
            ),
        )
        .order_by("-pushed_at", "-updated_at")
        .distinct()
    )

    mapping: dict[int, list[Repository]] = defaultdict(list)
    async for repository in repositories:
        for project in repository.prefetched_projects:
            mapping[project.pk].append(repository)

    return [mapping.get(project_id, []) for project_id in project_ids]


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
    releases = (
        Release.objects.filter(pk__in=release_ids)
        .select_related("repository")
        .prefetch_related(
            Prefetch(
                "repository__project_set",
                queryset=Project.objects.only("name"),
                to_attr="prefetched_projects",
            )
        )
    )
    mapping: dict[int, str | None] = {}
    async for release in releases:
        mapping[release.pk] = (
            release.repository.prefetched_projects[0].name.removeprefix(
                f"{OWASP_ORGANIZATION_NAME} "
            )
            if release.repository and release.repository.prefetched_projects
            else None
        )

    return [mapping.get(release_id) for release_id in release_ids]


def get_repository_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        REPOSITORY_BY_RELEASE_ID_LOADER: DataLoader[int, Repository | None](
            load_fn=load_repositories_by_release_id,
        ),
        REPOSITORY_PROJECT_NAME_BY_RELEASE_ID_LOADER: DataLoader[int, str | None](
            load_fn=load_repository_project_names_by_release_id,
        ),
        REPOSITORIES_BY_PROJECT_ID: DataLoader[int, list[Repository]](
            load_fn=load_repositories_by_project_id,
        ),
    }
