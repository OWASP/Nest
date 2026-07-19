"""Dataloaders for pull requests."""

from collections import defaultdict

from django.db.models import Prefetch
from strawberry.dataloader import DataLoader

from apps.github.models.pull_request import PullRequest
from apps.owasp.models.project import Project

RECENT_PULL_REQUESTS_BY_PROJECT_ID = "recent_pull_requests_by_project_id"


async def load_recent_pull_requests_by_project_id(
    keys: list[tuple[int, int]],
) -> list[list[PullRequest]]:
    """Batch-load recent pull requests across the given projects' repositories."""
    if not keys:
        return []

    project_ids = [key[0] for key in keys]
    limit = keys[0][1]

    pull_requests = (
        PullRequest.objects.filter(repository__project__in=project_ids)
        .prefetch_related(
            Prefetch(
                "repository__project_set",
                queryset=Project.objects.filter(pk__in=project_ids).only("pk"),
                to_attr="prefetched_projects",
            ),
        )
        .order_by("-created_at")
        .distinct()
    )

    mapping: dict[int, list[PullRequest]] = defaultdict(list)
    async for pull_request in pull_requests:
        for project in pull_request.repository.prefetched_projects:
            if len(mapping[project.pk]) < limit:
                mapping[project.pk].append(pull_request)

    return [mapping.get(project_id, []) for project_id in project_ids]


def get_pull_request_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        RECENT_PULL_REQUESTS_BY_PROJECT_ID: DataLoader[tuple[int, int], list[PullRequest]](
            load_fn=load_recent_pull_requests_by_project_id
        ),
    }
