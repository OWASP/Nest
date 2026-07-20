"""Tests for shared dataloader utility functions."""

from types import SimpleNamespace
from typing import cast

import pytest
from django.db.models import QuerySet

from apps.common.api.internal.dataloaders.utils import (
    get_m2m_results_by_keys,
    get_result_by_keys,
    get_results_by_keys,
    get_values_by_keys,
)


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


def make_m2m_item(m2m_field: str, related_items: list, **kwargs):
    """Create an item whose ``m2m_field.all()`` yields ``related_items`` asynchronously."""

    async def _agen():
        for item in related_items:
            yield item

    return SimpleNamespace(**{m2m_field: SimpleNamespace(all=_agen)}, **kwargs)


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


class TestValuesByKeys:
    """Tests for get_values_by_keys."""

    @pytest.mark.asyncio
    async def test_basic_mapping(self):
        """Each key maps to exactly one value."""
        pairs = async_gen([(1, "a"), (2, "b")])
        result = await get_values_by_keys(pairs, [1, 2], default="")
        assert result == ["a", "b"]

    @pytest.mark.asyncio
    async def test_empty_pairs(self):
        """Empty pairs returns the default for every key."""
        result = await get_values_by_keys(async_gen([]), [1, 2, 3], default=0)
        assert result == [0, 0, 0]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """Empty keys list returns an empty list regardless of pairs content."""
        result = await get_values_by_keys(async_gen([(1, "a")]), [], default="")
        assert result == []

    @pytest.mark.asyncio
    async def test_key_absent_from_pairs(self):
        """A key with no matching pair gets the default."""
        pairs = async_gen([(1, "a")])
        result = await get_values_by_keys(pairs, [1, 2], default="none")
        assert result == ["a", "none"]

    @pytest.mark.asyncio
    async def test_order_matches_keys_not_pairs(self):
        """The output order follows ``keys``, not the pairs iteration order."""
        pairs = async_gen([(3, "c"), (1, "a"), (2, "b")])
        result = await get_values_by_keys(pairs, [1, 2, 3], default="")
        assert result == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_pairs_not_in_keys_are_ignored(self):
        """Pairs whose key is not present in ``keys`` are silently discarded."""
        pairs = async_gen([(1, "a"), (99, "orphan")])
        result = await get_values_by_keys(pairs, [1], default="")
        assert result == ["a"]

    @pytest.mark.asyncio
    async def test_duplicate_keys_in_keys_list(self):
        """A key appearing multiple times in ``keys`` produces one entry per occurrence."""
        pairs = async_gen([(1, "a")])
        result = await get_values_by_keys(pairs, [1, 1], default="")
        assert result == ["a", "a"]

    @pytest.mark.asyncio
    async def test_later_value_overwrites_earlier(self):
        """When the same key appears twice, the last value wins."""
        pairs = async_gen([(1, "a"), (1, "b")])
        result = await get_values_by_keys(pairs, [1], default="")
        assert result == ["b"]

    @pytest.mark.asyncio
    async def test_default_is_used_for_missing_keys(self):
        """The default value is used for any key without a matching pair."""
        pairs = async_gen([(1, 100)])
        result = await get_values_by_keys(pairs, [1, 2, 3], default=-1)
        assert result == [100, -1, -1]

    @pytest.mark.parametrize(
        ("pairs", "keys", "default", "expected"),
        [
            (
                [(10, "alpha")],
                [10],
                "",
                ["alpha"],
            ),
            (
                [],
                [10, 20],
                "none",
                ["none", "none"],
            ),
            (
                [(2, "y"), (1, "x")],
                [2, 1],
                "",
                ["y", "x"],
            ),
            (
                [(1, 5), (1, 9)],
                [1],
                0,
                [9],
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_parametrized_scenarios(self, pairs, keys, default, expected):
        """Parametrized spot-checks covering single value, empty, ordered, and overwrite cases."""
        result = await get_values_by_keys(async_gen(pairs), keys, default=default)
        assert result == expected


class TestResultByKeys:
    """Tests for get_result_by_keys."""

    @pytest.mark.asyncio
    async def test_basic_mapping(self):
        """Each key maps to exactly one value."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=2, repo="repo-b"),
        ]
        result = await get_result_by_keys(make_qs(items), [1, 2], "org_id", "repo")
        assert result == ["repo-a", "repo-b"]

    @pytest.mark.asyncio
    async def test_empty_queryset(self):
        """Empty queryset returns None for every key."""
        result = await get_result_by_keys(make_qs([]), [1, 2, 3], "org_id", "repo")
        assert result == [None, None, None]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """Empty keys list returns an empty list."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_result_by_keys(make_qs(items), [], "org_id", "repo")
        assert result == []

    @pytest.mark.asyncio
    async def test_key_absent_from_results(self):
        """A key with no matching item returns None."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_result_by_keys(make_qs(items), [1, 2], "org_id", "repo")
        assert result == ["repo-a", None]

    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self):
        """The output order follows ``keys``, not the queryset iteration order."""
        items = [
            make_item(org_id=3, repo="repo-c"),
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=2, repo="repo-b"),
        ]
        result = await get_result_by_keys(make_qs(items), [1, 2, 3], "org_id", "repo")
        assert result == ["repo-a", "repo-b", "repo-c"]

    @pytest.mark.asyncio
    async def test_items_not_in_keys_are_ignored(self):
        """Items whose key is not present in ``keys`` are silently discarded."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=99, repo="orphan"),
        ]
        result = await get_result_by_keys(make_qs(items), [1], "org_id", "repo")
        assert result == ["repo-a"]

    @pytest.mark.asyncio
    async def test_duplicate_keys_in_keys_list(self):
        """A key appearing multiple times in ``keys`` produces one entry per occurrence."""
        items = [make_item(org_id=1, repo="repo-a")]
        result = await get_result_by_keys(make_qs(items), [1, 1], "org_id", "repo")
        assert result == ["repo-a", "repo-a"]

    @pytest.mark.asyncio
    async def test_value_field_none_returns_whole_item(self):
        """When value_field is None, the queryset item itself is the value."""
        items = [
            make_item(pk=1, name="alpha"),
            make_item(pk=2, name="beta"),
        ]
        result = await get_result_by_keys(make_qs(items), [1, 2], "pk")
        assert result == [items[0], items[1]]

    @pytest.mark.asyncio
    async def test_later_value_overwrites_earlier(self):
        """When single=True, the last item for a key wins (overwrite, not append)."""
        items = [
            make_item(org_id=1, repo="repo-a"),
            make_item(org_id=1, repo="repo-b"),
        ]
        result = await get_result_by_keys(make_qs(items), [1], "org_id", "repo")
        assert result == ["repo-b"]

    @pytest.mark.parametrize(
        ("items", "keys", "key_field", "value_field", "expected"),
        [
            (
                [make_item(pk=10, name="alpha")],
                [10],
                "pk",
                "name",
                ["alpha"],
            ),
            (
                [],
                [10, 20],
                "pk",
                "name",
                [None, None],
            ),
            (
                [make_item(pk=1, name="x"), make_item(pk=2, name="y")],
                [2, 1],
                "pk",
                "name",
                ["y", "x"],
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_parametrized_scenarios(self, items, keys, key_field, value_field, expected):
        """Parametrized spot-checks covering single value, empty, and ordered cases."""
        result = await get_result_by_keys(make_qs(items), keys, key_field, value_field)
        assert result == expected


class TestM2mResultsByKeys:
    """Tests for get_m2m_results_by_keys."""

    @pytest.mark.asyncio
    async def test_basic_mapping(self):
        """Each key maps to the source items that have a matching related item."""
        items = [
            make_m2m_item("programs", [make_item(pk=1)], name="admin-a"),
            make_m2m_item("programs", [make_item(pk=2)], name="admin-b"),
        ]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 2], "programs", "pk", "name")
        assert result == [["admin-a"], ["admin-b"]]

    @pytest.mark.asyncio
    async def test_empty_queryset(self):
        """Empty queryset returns an empty list for every key."""
        result = await get_m2m_results_by_keys(make_qs([]), [1, 2], "programs", "pk", "name")
        assert result == [[], []]

    @pytest.mark.asyncio
    async def test_empty_keys(self):
        """Empty keys list returns an empty list regardless of queryset content."""
        items = [make_m2m_item("programs", [make_item(pk=1)], name="admin")]
        result = await get_m2m_results_by_keys(make_qs(items), [], "programs", "pk", "name")
        assert result == []

    @pytest.mark.asyncio
    async def test_key_absent_from_results(self):
        """A key with no matching related item gets an empty list."""
        items = [make_m2m_item("programs", [make_item(pk=1)], name="admin-a")]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 2], "programs", "pk", "name")
        assert result == [["admin-a"], []]

    @pytest.mark.asyncio
    async def test_multiple_items_per_key(self):
        """Multiple source items sharing the same related key are collected."""
        items = [
            make_m2m_item("programs", [make_item(pk=1)], name="admin-a"),
            make_m2m_item("programs", [make_item(pk=1)], name="admin-b"),
            make_m2m_item("programs", [make_item(pk=2)], name="admin-c"),
        ]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 2], "programs", "pk", "name")
        assert result == [["admin-a", "admin-b"], ["admin-c"]]

    @pytest.mark.asyncio
    async def test_multiple_related_per_source(self):
        """One source item related to multiple keys contributes to each."""
        items = [
            make_m2m_item(
                "programs",
                [make_item(pk=1), make_item(pk=2)],
                name="shared-admin",
            ),
        ]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 2], "programs", "pk", "name")
        assert result == [["shared-admin"], ["shared-admin"]]

    @pytest.mark.asyncio
    async def test_order_matches_keys_not_queryset(self):
        """The output order follows ``keys``, not the queryset iteration order."""
        items = [
            make_m2m_item("programs", [make_item(pk=3)], name="admin-c"),
            make_m2m_item("programs", [make_item(pk=1)], name="admin-a"),
            make_m2m_item("programs", [make_item(pk=2)], name="admin-b"),
        ]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 2, 3], "programs", "pk", "name")
        assert result == [["admin-a"], ["admin-b"], ["admin-c"]]

    @pytest.mark.asyncio
    async def test_items_not_in_keys_ignored(self):
        """Source items whose related key is not in ``keys`` are discarded."""
        items = [
            make_m2m_item("programs", [make_item(pk=1)], name="admin-a"),
            make_m2m_item("programs", [make_item(pk=99)], name="orphan"),
        ]
        result = await get_m2m_results_by_keys(make_qs(items), [1], "programs", "pk", "name")
        assert result == [["admin-a"]]

    @pytest.mark.asyncio
    async def test_duplicate_keys_in_keys_list(self):
        """A key appearing multiple times in ``keys`` produces one entry per occurrence."""
        items = [make_m2m_item("programs", [make_item(pk=1)], name="admin")]
        result = await get_m2m_results_by_keys(make_qs(items), [1, 1], "programs", "pk", "name")
        assert result == [["admin"], ["admin"]]

    @pytest.mark.asyncio
    async def test_value_field_none_returns_whole_item(self):
        """When value_field is None, the source item itself is the value."""
        item = make_m2m_item("programs", [make_item(pk=1)], name="alpha")
        result = await get_m2m_results_by_keys(make_qs([item]), [1], "programs", "pk")
        assert result == [[item]]

    @pytest.mark.parametrize(
        ("desc", "items", "keys", "m2m_field", "key_field", "value_field", "expected"),
        [
            (
                "single source, single related",
                [make_m2m_item("groups", [make_item(gid=10)], label="a")],
                [10],
                "groups",
                "gid",
                "label",
                [["a"]],
            ),
            (
                "empty queryset",
                [],
                [10, 20],
                "groups",
                "gid",
                "label",
                [[], []],
            ),
            (
                "multiple sources, reversed key order",
                [
                    make_m2m_item("groups", [make_item(gid=2)], label="y"),
                    make_m2m_item("groups", [make_item(gid=1)], label="x"),
                ],
                [2, 1],
                "groups",
                "gid",
                "label",
                [["y"], ["x"]],
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_parametrized_scenarios(
        self, desc, items, keys, m2m_field, key_field, value_field, expected
    ):
        """Parametrized spot-checks covering single, empty, and ordered cases."""
        result = await get_m2m_results_by_keys(
            make_qs(items), keys, m2m_field, key_field, value_field
        )
        assert result == expected
