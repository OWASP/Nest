"""Shared utilities for GraphQL dataloaders."""

from collections import defaultdict
from typing import cast

from django.db.models import Model, QuerySet


async def get_first_by_m2m_keys[K, V](
    model: type[Model],
    m2m_field: str,
    target_ids: set[K],
    target_fk_field: str,
    source_select_related: str,
    value_field: str | None = None,
) -> dict[K, V | None]:
    """Map target IDs to first matching source model value via an M2M through table.

    Args:
        model: The source model containing the M2M field.
        m2m_field: The name of the M2M field on the source model.
        target_ids: IDs of the target model to filter by.
        target_fk_field: The FK field name on the through table pointing to
            the target model.
        source_select_related: The select_related path on the through table
            pointing to the source model.
        value_field: The attribute on the source model to extract.
            When ``None``, the source model instance is used.

    Returns:
        A dict mapping each target ID to the first matching value or None.

    """
    mapping: dict[K, V | None] = {}
    through_model = getattr(model, m2m_field).through
    async for row in through_model.objects.filter(
        **{f"{target_fk_field}__in": target_ids}
    ).select_related(source_select_related):
        source = getattr(row, source_select_related)
        key: K = cast("K", getattr(row, target_fk_field))
        if key not in mapping:
            mapping[key] = cast(
                "V", source if value_field is None else getattr(source, value_field)
            )

    return mapping


async def get_results_by_keys[K, V](
    queryset: QuerySet[Model],
    keys: list[K],
    key_field: str,
    value_field: str | None = None,
) -> list[list[V]]:
    """Map a grouped-results dict back to an ordered list matching ``keys``.

    Args:
        queryset: The queryset to iterate over.
        keys: A list of keys to map the results to, in the desired order.
        key_field: The name of the attribute on each item that contains the key.
        value_field: The name of the attribute on each item that contains the value.
            When ``None``, the queryset item itself is used as the value.

    Returns:
        A list of result-lists, one per key, in the same order as ``keys``.

    """
    mapping: dict[K, list[V]] = defaultdict(list)
    async for item in queryset:
        key: K = cast("K", getattr(item, key_field))
        mapping[key].append(cast("V", item if value_field is None else getattr(item, value_field)))

    return [mapping.get(key, []) for key in keys]


async def get_result_by_keys[K, V](
    queryset: QuerySet[Model],
    keys: list[K],
    key_field: str,
    value_field: str | None = None,
) -> list[V | None]:
    """Map a single-result dict back to an ordered list matching ``keys``.

    Args:
        queryset: The queryset to iterate over.
        keys: A list of keys to map the results to, in the desired order.
        key_field: The name of the attribute on each item that contains the key.
        value_field: The name of the attribute on each item that contains the value.
            When ``None``, the queryset item itself is used as the value.

    Returns:
        A list of ``V | None``, one per key, in the same order as ``keys``.

    """
    mapping: dict[K, V] = {}
    async for item in queryset:
        key: K = cast("K", getattr(item, key_field))
        mapping[key] = cast("V", item if value_field is None else getattr(item, value_field))

    return [mapping.get(key) for key in keys]
