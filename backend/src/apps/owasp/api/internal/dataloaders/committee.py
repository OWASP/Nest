"""DataLoaders for committees."""

from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from strawberry.dataloader import DataLoader

from apps.common.api.internal.dataloaders.utils import get_results_by_keys
from apps.owasp.models.committee import Committee
from apps.owasp.models.entity_channel import EntityChannel
from apps.owasp.models.entity_member import EntityMember

ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER = "entity_channels_by_committee_id"
ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER = "entity_leaders_by_committee_id"


async def load_entity_channels_by_committee_id(
    committee_ids: list[int],
) -> list[list[EntityChannel]]:
    """Batch-load entity channels for the given committee IDs in a single query."""
    committee_content_type = await sync_to_async(ContentType.objects.get_for_model)(Committee)
    channels = EntityChannel.objects.filter(
        entity_type=committee_content_type,
        entity_id__in=committee_ids,
        is_active=True,
        is_reviewed=True,
    )
    return await get_results_by_keys(channels, committee_ids, key_field="entity_id")


async def load_entity_leaders_by_committee_id(
    committee_ids: list[int],
) -> list[list[EntityMember]]:
    """Batch-load entity leaders for the given committee IDs in a single query."""
    committee_content_type = await sync_to_async(ContentType.objects.get_for_model)(Committee)
    leaders = (
        EntityMember.objects.select_related("member")
        .filter(
            entity_type=committee_content_type,
            entity_id__in=committee_ids,
            role=EntityMember.Role.LEADER,
            is_active=True,
            is_reviewed=True,
        )
        .order_by("order")
    )
    return await get_results_by_keys(leaders, committee_ids, key_field="entity_id")


def get_committee_loaders() -> dict[str, object]:
    """Return a mapping of per-request DataLoader instances."""
    return {
        ENTITY_CHANNELS_BY_COMMITTEE_ID_LOADER: DataLoader[int, list[EntityChannel]](
            load_fn=load_entity_channels_by_committee_id,
        ),
        ENTITY_LEADERS_BY_COMMITTEE_ID_LOADER: DataLoader[int, list[EntityMember]](
            load_fn=load_entity_leaders_by_committee_id,
        ),
    }
