"""DataLoaders for projects."""

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from django.db.models import F, Window
from django.db.models.functions import RowNumber
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import (
    get_m2m_results_by_keys,
    get_result_by_keys,
    get_results_by_keys,
)
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.entity_member import EntityMember
from apps.owasp.models.project import Project
from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

ENTITY_CHANNELS_BY_PROJECT_ID = "entity_channels_by_project_id"
ENTITY_LEADERS_BY_PROJECT_ID = "entity_leaders_by_project_id"
HEALTH_METRICS_LATEST_BY_PROJECT_ID = "health_metrics_latest_by_project_id"
HEALTH_METRICS_LIST_BY_PROJECT_ID = "health_metrics_list_by_project_id"
PROJECT_BY_REPOSITORY_ID = "project_by_repository_id"


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


async def load_health_metrics_list_by_project_id(
    keys: list[tuple[int, int]],
) -> list[list[ProjectHealthMetrics]]:
    """Batch-load the N most recent health metrics per project in a single query.

    Returns each project's metrics in chronological order (oldest to newest)
    so charts display correctly from left to right.
    """
    if not keys:
        return []

    project_ids = [key[0] for key in keys]
    limit = keys[0][1]

    metrics = (
        ProjectHealthMetrics.objects.filter(project_id__in=project_ids)
        .annotate(
            row_number=Window(
                expression=RowNumber(),
                partition_by=[F("project_id")],
                order_by=F("nest_created_at").desc(),
            )
        )
        .filter(row_number__lte=limit)
        .order_by("project_id", "nest_created_at")
    )

    return await get_results_by_keys(metrics, project_ids, key_field="project_id")


async def load_health_metrics_latest_by_project_id(
    project_ids: list[int],
) -> list[ProjectHealthMetrics | None]:
    """Batch-load the latest health metrics per project in a single query."""
    metrics = (
        ProjectHealthMetrics.objects.filter(project_id__in=project_ids)
        .distinct("project_id")
        .order_by("project_id", "-nest_created_at")
    )

    return await get_result_by_keys(metrics, project_ids, key_field="project_id")


async def load_entity_channels_by_project_id(
    project_ids: list[int],
) -> list[list[EntityChannel]]:
    """Batch-load entity channels for the given project IDs in a single query."""
    project_content_type = await sync_to_async(ContentType.objects.get_for_model)(Project)
    channels = EntityChannel.objects.filter(
        entity_type=project_content_type,
        entity_id__in=project_ids,
        is_active=True,
        is_reviewed=True,
    )
    return await get_results_by_keys(channels, project_ids, key_field="entity_id")


async def load_entity_leaders_by_project_id(
    project_ids: list[int],
) -> list[list[EntityMember]]:
    """Batch-load entity leaders for the given project IDs in a single query."""
    project_content_type = await sync_to_async(ContentType.objects.get_for_model)(Project)
    leaders = (
        EntityMember.objects.select_related("member")
        .filter(
            entity_type=project_content_type,
            entity_id__in=project_ids,
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        .order_by("order")
    )
    return await get_results_by_keys(leaders, project_ids, key_field="entity_id")


def get_project_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ENTITY_CHANNELS_BY_PROJECT_ID: DataLoader[int, list[EntityChannel]](
            load_fn=load_entity_channels_by_project_id,
        ),
        ENTITY_LEADERS_BY_PROJECT_ID: DataLoader[int, list[EntityMember]](
            load_fn=load_entity_leaders_by_project_id,
        ),
        HEALTH_METRICS_LATEST_BY_PROJECT_ID: DataLoader[int, ProjectHealthMetrics | None](
            load_fn=load_health_metrics_latest_by_project_id,
        ),
        HEALTH_METRICS_LIST_BY_PROJECT_ID: DataLoader[tuple[int, int], list[ProjectHealthMetrics]](
            load_fn=load_health_metrics_list_by_project_id
        ),
        PROJECT_BY_REPOSITORY_ID: DataLoader[int, Project | None](
            load_fn=load_projects_by_repository_id,
        ),
    }
