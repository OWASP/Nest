"""Shared utilities for GraphQL dataloaders."""

from collections import defaultdict
from typing import cast

from django.db.models import Model, QuerySet


async def get_results_by_keys[K, V](
    queryset: QuerySet[Model], keys: list[K], key_field: str, value_field: str
) -> list[list[V]]:
    """Map a grouped-results dict back to an ordered list matching ``keys``.

    Args:
        queryset: The queryset to iterate over.
        keys: A list of keys to map the results to, in the desired order.
        key_field: The name of the attribute on each item that contains the key.
        value_field: The name of the attribute on each item that contains the value.

    Returns:
        A list of result-lists, one per key, in the same order as ``keys``.

    """
    mapping: dict[K, list[V]] = defaultdict(list)
    async for item in queryset:
        key: K = cast("K", getattr(item, key_field))
        value: V = cast("V", getattr(item, value_field))
        mapping[key].append(value)

    return [mapping.get(key, []) for key in keys]
