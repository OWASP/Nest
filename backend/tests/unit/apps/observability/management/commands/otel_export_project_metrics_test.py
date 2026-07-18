"""Tests for the otel_export_project_metrics command."""

import json
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

COMMAND_PATH = "apps.observability.management.commands.otel_export_project_metrics"


def _row(when, stars, forks, contributors):
    """Build an in-memory ProjectHealthMetrics row."""
    row = ProjectHealthMetrics(
        stars_count=stars, forks_count=forks, contributors_count=contributors
    )
    row.nest_created_at = when
    return row


class TestOtelExportProjectMetricsCommand:
    def test_errors_when_import_url_missing(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = ""
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        stderr = StringIO()
        call_command("otel_export_project_metrics", stderr=stderr)

        assert "OTEL_METRICS_IMPORT_URL is not set" in stderr.getvalue()
        post.assert_not_called()

    def test_errors_on_invalid_batch_size(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = "https://vm:8428"
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        stderr = StringIO()
        call_command("otel_export_project_metrics", "--batch-size", "0", stderr=stderr)

        assert "--batch-size must be a positive integer" in stderr.getvalue()
        post.assert_not_called()

    def test_backfill_posts_nest_history_to_victoriametrics(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = "https://vm:8428"
        first = timezone.make_aware(timezone.datetime(2025, 1, 1))
        second = timezone.make_aware(timezone.datetime(2025, 1, 2))
        rows = [
            _row(first, stars=10, forks=2, contributors=5),
            _row(second, stars=12, forks=3, contributors=6),
        ]

        objects = mocker.patch(f"{COMMAND_PATH}.ProjectHealthMetrics.objects")
        objects.filter.return_value.order_by.return_value.iterator.return_value = iter(rows)
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        call_command("otel_export_project_metrics", "--all")

        objects.filter.assert_called_once_with(project__key="www-project-nest")
        post.assert_called_once()
        assert post.call_args.args[0] == "https://vm:8428/api/v1/import"

        lines = [json.loads(line) for line in post.call_args.kwargs["data"].splitlines()]
        by_series = {m["metric"]["__name__"]: m for m in lines}

        assert all(m["metric"]["project"] == "nest" for m in lines)
        stars = by_series["nest.project.stars"]
        assert stars["values"] == [10, 12]
        assert stars["timestamps"] == [
            int(first.timestamp() * 1000),
            int(second.timestamp() * 1000),
        ]
        assert by_series["nest.project.forks"]["values"] == [2, 3]
        assert by_series["nest.project.contributors"]["values"] == [5, 6]

    def test_default_mode_exports_latest_day(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = "https://vm:8428"
        latest = timezone.make_aware(timezone.datetime(2025, 1, 2))
        rows = [_row(latest, stars=12, forks=3, contributors=6)]

        objects = mocker.patch(f"{COMMAND_PATH}.ProjectHealthMetrics.objects")
        ordered = objects.filter.return_value.order_by.return_value
        ordered.aggregate.return_value = {"latest": latest}
        ordered.filter.return_value.iterator.return_value = iter(rows)
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        call_command("otel_export_project_metrics")

        ordered.filter.assert_called_once()
        post.assert_called_once()

    def test_warns_when_no_metrics_exist(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = "https://vm:8428"
        objects = mocker.patch(f"{COMMAND_PATH}.ProjectHealthMetrics.objects")
        objects.filter.return_value.order_by.return_value.aggregate.return_value = {"latest": None}
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        stdout = StringIO()
        call_command("otel_export_project_metrics", stdout=stdout)

        assert "No Nest project health metrics found" in stdout.getvalue()
        post.assert_not_called()

    def test_backfill_warns_when_no_rows(self, settings, mocker):
        settings.OTEL_METRICS_IMPORT_URL = "https://vm:8428"
        objects = mocker.patch(f"{COMMAND_PATH}.ProjectHealthMetrics.objects")
        objects.filter.return_value.order_by.return_value.iterator.return_value = iter([])
        post = mocker.patch(f"{COMMAND_PATH}.requests.post")

        stdout = StringIO()
        call_command("otel_export_project_metrics", "--all", stdout=stdout)

        assert "No Nest project health metrics found" in stdout.getvalue()
        post.assert_not_called()
