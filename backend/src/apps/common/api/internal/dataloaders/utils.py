"""Shared utilities for GraphQL dataloaders."""

from collections import defaultdict
from collections.abc import AsyncIterable
from typing import cast

from django.db.models import Model, QuerySet


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


async def get_values_by_keys[K, V](
    pairs: AsyncIterable[tuple[K, V]],
    keys: list[K],
    default: V,
) -> tuple[V, ...]:
    """Map async-iterated key/value pairs to an ordered list matching ``keys``.

    Args:
        pairs: An async iterable yielding (key, value) tuples.
        keys: A list of keys to map the results to, in the desired order.
        default: The value to use for keys that have no match.

    Returns:
        A tuple of ``V``, one per key, in the same order as ``keys``.

    """
    mapping = {key: value async for key, value in pairs}

    return tuple(mapping.get(key, default) for key in keys)


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


async def get_m2m_results_by_keys[K, V](
    queryset: QuerySet[Model],
    keys: list[K],
    m2m_field: str,
    key_field: str,
    value_field: str | None = None,
) -> list[list[V]]:
    """Map M2M-related results back to an ordered list matching ``keys``.

    Args:
        queryset: The queryset of source objects to iterate over.
        keys: A list of keys to map the results to, in the desired order.
        m2m_field: The name of the M2M field on each source object.
        key_field: The name of the attribute on each related object that contains the key.
        value_field: The name of the attribute on each source object that contains the value.
            When ``None``, the source object itself is used as the value.

    Returns:
        A list of result-lists, one per key, in the same order as ``keys``.

    """
    mapping: dict[K, list[V]] = defaultdict(list)
    async for item in queryset:
        related_manager = getattr(item, m2m_field)
        async for related in related_manager.all():
            key: K = cast("K", getattr(related, key_field))
            mapping[key].append(
                cast("V", item if value_field is None else getattr(item, value_field))
            )

    return [mapping.get(key, []) for key in keys]
