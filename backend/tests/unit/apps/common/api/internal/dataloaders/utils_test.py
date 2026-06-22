"""Tests for shared dataloader utility functions."""

from types import SimpleNamespace
from typing import cast

import pytest
from django.db.models import QuerySet

from apps.common.api.internal.dataloaders.utils import get_results_by_keys


async def async_gen(items):
    """Yield items one-by-one as an async generator."""
    for item in items:
        yield item


def make_qs(items) -> QuerySet:
    """Wrap a list in an async-iterable that satisfies the QuerySet type annotation."""
    return cast("QuerySet", async_gen(items))


def make_item(**kwargs):
    """Return a simple namespace object with the given attributes."""
    return SimpleNamespace(**kwargs)


class TestResultsByKeys:
    """Tests for get_results_by_keys."""

    @pytest.mark.asyncio
    async def test_basic_mapping(self):
        """Each key maps to exactly one value."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=2, repo="repo-b"),
        ]
        result = await get_results_by_keys(make_qs(items), [1, 2], "org_id", "repo")
        assert result == [["repo-a"], ["repo-b"]]

    @pytest.mark.asyncio
    async def test_empty_queryset(self):
        """Empty queryset returns an empty list for every key."""
        result = await get_results_by_keys(make_qs([]), [1, 2, 3], "org_id", "repo")
        assert result == [[], [], []]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """Empty keys list returns an empty list regardless of queryset content."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_results_by_keys(make_qs(items), [], "org_id", "repo")
        assert result == []

    @pytest.mark.asyncio
    async def test_key_absent_from_results(self):
        """A key with no matching queryset items gets an empty list."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_results_by_keys(make_qs(items), [1, 2], "org_id", "repo")
        assert result == [["repo-a"], []]

    @pytest.mark.asyncio
    async def test_multiple_values_per_key(self):
        """Multiple items sharing the same key are collected into one list."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=1, repo="repo-b"),
            make_item(org_id=2, repo="repo-c"),
        ]
        result = await get_results_by_keys(make_qs(items), [1, 2], "org_id", "repo")
        assert result == [["repo-a", "repo-b"], ["repo-c"]]

    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self):
        """The output order follows ``keys``, not the queryset iteration order."""
        items = [
            make_item(org_id=3, repo="repo-c"),
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=2, repo="repo-b"),
        ]
        result = await get_results_by_keys(make_qs(items), [1, 2, 3], "org_id", "repo")
        assert result == [["repo-a"], ["repo-b"], ["repo-c"]]

    @pytest.mark.asyncio
    async def test_items_not_in_keys_are_ignored(self):
        """Items whose key is not present in ``keys`` are silently discarded."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=99, repo="orphan"),  # key 99 is not requested
        ]
        result = await get_results_by_keys(make_qs(items), [1], "org_id", "repo")
        assert result == [["repo-a"]]

    @pytest.mark.asyncio
    async def test_arbitrary_field_names(self):
        """key_field and value_field are applied via getattr, so any attribute names work."""
        items = [
            make_item(chapter_id="us", city="New York"),
            make_item(chapter_id="us", city="San Francisco"),
            make_item(chapter_id="uk", city="London"),
        ]
        result = await get_results_by_keys(make_qs(items), ["uk", "us"], "chapter_id", "city")
        assert result == [["London"], ["New York", "San Francisco"]]

    @pytest.mark.asyncio
    async def test_duplicate_keys_in_keys_list(self):
        """A key appearing multiple times in ``keys`` produces one entry per occurrence."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_results_by_keys(make_qs(items), [1, 1], "org_id", "repo")
        assert result == [["repo-a"], ["repo-a"]]

    @pytest.mark.asyncio
    async def test_value_field_none_returns_whole_item(self):
        """When value_field is None, the queryset item itself is the value."""
        items = [
            make_item(pk=1, name="alpha"),
            make_item(pk=2, name="beta"),
        ]
        result = await get_results_by_keys(make_qs(items), [1, 2], "pk")
        assert result == [[items[0]], [items[1]]]

    @pytest.mark.parametrize(
        ("items", "keys", "key_field", "value_field", "expected"),
        [
            (
                [make_item(pk=10, name="alpha")],
                [10],
                "pk",
                "name",
                [["alpha"]],
            ),
            (
                [],
                [10, 20],
                "pk",
                "name",
                [[], []],
            ),
            (
                [make_item(pk=1, name="x"), make_item(pk=1, name="y"), make_item(pk=2, name="z")],
                [2, 1],
                "pk",
                "name",
                [["z"], ["x", "y"]],
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_parametrized_scenarios(self, items, keys, key_field, value_field, expected):
        """Parametrized spot-checks covering single value, empty, and multi-value cases."""
        result = await get_results_by_keys(make_qs(items), keys, key_field, value_field)
        assert result == expected
