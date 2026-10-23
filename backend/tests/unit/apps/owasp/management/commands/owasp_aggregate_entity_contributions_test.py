"""Tests for consistent chapter and project contribution reports."""

from argparse import ArgumentParser
from datetime import UTC, date, datetime, timedelta
from datetime import timezone as datetime_timezone
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from django.db.models import QuerySet
from django.utils import timezone

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.owasp.management.commands.owasp_aggregate_entity_contributions import Command
from apps.owasp.models import Chapter, Project

END_AT = datetime(2026, 10, 22, 12, 30, 45, 123456, tzinfo=UTC)
START_AT = END_AT - timedelta(days=365)
EVENTS = (
    (Commit, "commits", "created_at"),
    (Issue, "issues", "created_at"),
    (PullRequest, "pull_requests", "created_at"),
    (Release, "releases", "published_at"),
)
GROUPS = {
    Commit: [{"day": date(2026, 10, 20), "count": 2}],
    Issue: [{"day": date(2026, 10, 20), "count": 3}],
    PullRequest: [{"day": date(2026, 10, 21), "count": 4}],
    Release: [{"day": date(2026, 10, 22), "count": 5}],
}


class MockQuerySet(list):
    """Entity selection without database access."""

    def filter(self, **kwargs):
        return MockQuerySet(
            item for item in self if all(getattr(item, k) == v for k, v in kwargs.items())
        )

    def order_by(self, *_fields):
        return self

    def select_related(self, *_fields):
        return self

    def prefetch_related(self, *_fields):
        return self


@pytest.fixture
def command():
    return Command()


@pytest.fixture(params=[Chapter, Project], ids=["chapter", "project"])
def entity(request):
    instance = mock.Mock(spec=request.param)
    instance.key = "test-entity"
    instance.owasp_repository = mock.Mock(id=1)
    if request.param is Project:
        instance.repositories.all.return_value = [mock.Mock(id=2), mock.Mock(id=1)]
    return instance


@pytest.mark.parametrize("days", [365, 90])
def test_command_arguments(command, days):
    parser = ArgumentParser()
    command.add_arguments(parser)
    arguments = ["--entity-type", "chapter"]
    if days != 365:
        arguments += ["--days", str(days)]
    options = parser.parse_args(arguments)
    assert options.days == days
    assert options.key is None
    assert options.offset == 0


def test_repository_selection_is_deduplicated(command, entity):
    expected = {1, 2} if isinstance(entity, Project) else {1}
    assert set(command._get_repository_ids(entity)) == expected


def test_report_groups_and_filters_all_events_in_postgresql(command, entity):
    """Compile the real ORM queries without requiring a database in unit-test CI."""
    queries = []

    def grouped_rows(queryset):
        sql, parameters = queryset.query.sql_with_params()
        lookups = {
            (lookup.lhs.target.name, lookup.lookup_name): lookup.rhs
            for lookup in queryset.query.where.children
        }
        queries.append((queryset.model, sql, parameters, lookups))
        return iter(GROUPS[queryset.model])

    with (
        timezone.override(ZoneInfo("Asia/Kolkata")),  # cspell:ignore Kolkata
        mock.patch.object(QuerySet, "__iter__", grouped_rows),
    ):
        daily, stats = command.aggregate_contributions(entity, START_AT, END_AT)

    assert daily == {"2026-10-20": 5, "2026-10-21": 4, "2026-10-22": 5}
    assert stats == {
        "commits": 2,
        "issues": 3,
        "pull_requests": 4,
        "releases": 5,
        "total": 14,
        "start_at": START_AT.isoformat(),
        "end_at": END_AT.isoformat(),
    }
    assert stats["total"] == sum(daily.values())
    assert len(queries) == len(EVENTS)
    for model, sql, parameters, lookups in queries:
        date_field = "published_at" if model is Release else "created_at"
        assert lookups[date_field, "gte"] == START_AT
        assert lookups[date_field, "lte"] == END_AT
        assert f'"{date_field}" >=' in sql
        assert f'"{date_field}" <=' in sql
        assert "AT TIME ZONE" in sql
        assert "UTC" in parameters
        assert START_AT in parameters
        assert END_AT in parameters
        assert "COUNT(" in sql
        assert "GROUP BY" in sql
        assert "ORDER BY" not in sql
        assert '"repository_id" IN' in sql
        if model is Release:
            assert 'NOT "github_releases"."is_draft"' in sql
        if model is PullRequest:
            assert '"state" =' not in sql
            assert '"merged_at"' not in sql


def test_empty_report_still_records_period(command, entity):
    entity.owasp_repository = None
    if isinstance(entity, Project):
        entity.repositories.all.return_value = []

    with mock.patch.object(command, "_aggregate_contribution_dates") as aggregate:
        daily, stats = command.aggregate_contributions(entity, START_AT, END_AT)

    aggregate.assert_not_called()
    assert daily == {}
    assert stats == {
        "commits": 0,
        "issues": 0,
        "pull_requests": 0,
        "releases": 0,
        "total": 0,
        "start_at": START_AT.isoformat(),
        "end_at": END_AT.isoformat(),
    }


@pytest.mark.parametrize("days", [365, 90])
def test_handle_uses_one_utc_clock_and_saves_both_fields(command, entity, days):
    model = Project if isinstance(entity, Project) else Chapter
    second = mock.Mock(spec=model)
    second.key = "second-entity"
    queryset = MockQuerySet([entity, second])
    daily = {"2026-10-20": 1}
    stats = {"total": 1, "start_at": "saved-start", "end_at": "saved-end"}
    local_end = END_AT.astimezone(datetime_timezone(timedelta(hours=5, minutes=30)))

    with (
        mock.patch.object(model.objects, "filter", return_value=queryset) as select,
        mock.patch.object(model, "bulk_save") as save,
        mock.patch.object(
            command, "aggregate_contributions", return_value=(daily, stats)
        ) as aggregate,
        mock.patch("django.utils.timezone.now", return_value=local_end) as clock,
    ):
        command.handle(entity_type=model.__name__.lower(), days=days, offset=0)

    clock.assert_called_once_with()
    select.assert_called_once_with(is_active=True)
    assert aggregate.call_args_list == [
        mock.call(item, END_AT - timedelta(days=days), END_AT) for item in queryset
    ]
    assert aggregate.call_args.args[1].tzinfo is UTC
    assert aggregate.call_args.args[2].tzinfo is UTC
    for item in queryset:
        assert item.contribution_data == daily
        assert item.contribution_stats == stats
    expected_fields = ["contribution_data", "contribution_stats"]
    if model is Chapter:
        expected_fields = tuple(expected_fields)
    save.assert_called_once_with(queryset, fields=expected_fields)


def test_handle_preserves_key_and_offset_filtering(command, entity):
    model = Project if isinstance(entity, Project) else Chapter
    skipped = mock.Mock(spec=model, key="other-entity")
    queryset = MockQuerySet([skipped, entity, entity])
    with (
        mock.patch.object(model.objects, "filter", return_value=queryset),
        mock.patch.object(model, "bulk_save") as save,
        mock.patch.object(command, "aggregate_contributions", return_value=({}, {})) as aggregate,
    ):
        command.handle(entity_type=model.__name__.lower(), key="test-entity", days=365, offset=1)
    aggregate.assert_called_once()
    assert aggregate.call_args.args[0] is entity
    save.assert_called_once()


@pytest.mark.parametrize("model", [Chapter, Project])
def test_handle_empty_selection_does_not_save(command, model):
    with (
        mock.patch.object(model.objects, "filter", return_value=MockQuerySet()),
        mock.patch.object(model, "bulk_save") as save,
    ):
        command.handle(entity_type=model.__name__.lower(), days=365, offset=0)
    save.assert_not_called()
