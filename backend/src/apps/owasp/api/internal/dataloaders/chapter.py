"""DataLoaders for chapters."""

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.entity_member import EntityMember

ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER = "entity_channels_by_chapter_id"
ENTITY_LEADERS_BY_CHAPTER_ID_LOADER = "entity_leaders_by_chapter_id"


async def load_entity_channels_by_chapter_id(
    chapter_ids: list[int],
) -> list[list[EntityChannel]]:
    """Batch-load entity channels for the given chapter IDs in a single query."""
    chapter_content_type = await sync_to_async(ContentType.objects.get_for_model)(Chapter)
    channels = EntityChannel.objects.filter(
        entity_type=chapter_content_type,
        entity_id__in=chapter_ids,
        is_active=True,
        is_reviewed=True,
    )
    return await get_results_by_keys(channels, chapter_ids, key_field="entity_id")


async def load_entity_leaders_by_chapter_id(
    chapter_ids: list[int],
) -> list[list[EntityMember]]:
    """Batch-load entity leaders for the given chapter IDs in a single query."""
    chapter_content_type = await sync_to_async(ContentType.objects.get_for_model)(Chapter)
    leaders = (
        EntityMember.objects.select_related("member")
        .filter(
            entity_type=chapter_content_type,
            entity_id__in=chapter_ids,
            role=EntityMember.Role.LEADER,
        )
        .order_by("order")
    )
    return await get_results_by_keys(leaders, chapter_ids, key_field="entity_id")


def get_chapter_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ENTITY_CHANNELS_BY_CHAPTER_ID_LOADER: DataLoader[int, list[EntityChannel]](
            load_fn=load_entity_channels_by_chapter_id,
        ),
        ENTITY_LEADERS_BY_CHAPTER_ID_LOADER: DataLoader[int, list[EntityMember]](
            load_fn=load_entity_leaders_by_chapter_id,
        ),
    }
