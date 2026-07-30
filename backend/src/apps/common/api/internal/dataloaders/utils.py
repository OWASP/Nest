"""Shared utilities for GraphQL dataloaders."""

from collections import defaultdict
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


async def get_top_contributors_by_keys[K](
    queryset: QuerySet[Model, dict[str, str | int]],
    keys: list[K],
    key_field: str,
) -> list[list[dict[str, str | int]]]:
    """Map top-contributor rows back to an ordered list of dicts matching ``keys``.

    Each queryset item is expected to expose the flat dict keys ``avatar_url``,
    ``login``, ``name`` and ``contributions_count`` (``.values()`` grouped rows,
    e.g. project-level contributors where contributions are summed across
    repositories).

    The produced dict structure is fixed across all top-contributor resolvers
    (repositories, projects, chapters, committees).

    Args:
        queryset: The queryset of (repository) contributors to iterate over.
        keys: A list of keys to map the results to, in the desired order.
        key_field: The name of the attribute (or dict key) on each item that
            contains the key.

    Returns:
        A list of contributor-dict lists, one per key, in the same order as
        ``keys``.

    """
    mapping: dict[K, list[dict[str, str | int]]] = defaultdict(list)
    async for item in queryset:
        key: K = cast("K", item[key_field])
        mapping[key].append(
            {
                "avatar_url": item["avatar_url"],
                "contributions_count": item["contributions_count"],
                "id": item["login"],
                "login": item["login"],
                "name": item["name"],
            }
        )

    return [mapping.get(key, []) for key in keys]
