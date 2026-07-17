"""Export OWASP project health metrics history to VictoriaMetrics.

`ProjectHealthMetrics` stores a daily snapshot per project (stars, forks,
contributors). This command copies that history into VictoriaMetrics using each
row's date as the sample timestamp, so the metrics show changes over time.

It writes directly to VictoriaMetrics' JSON import API rather than through the
OpenTelemetry pipeline, because OTel stamps every sample with the current time
and cannot represent historical values.

Modes:
  --all   export the full history (one-time backfill)
  default export only the latest snapshot day (for a daily run)
"""

import json
from collections import defaultdict

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

# VM metric name -> ProjectHealthMetrics field
METRIC_FIELDS = {
    "nest.project.stars": "stars_count",
    "nest.project.forks": "forks_count",
    "nest.project.contributors": "contributors_count",
}

REQUEST_TIMEOUT = 30


class Command(BaseCommand):
    help = "Export project health metrics history to VictoriaMetrics."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Export the full history (backfill). Default exports only the latest day.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of series sent per import request.",
        )

    def handle(self, *args, **options):
        base_url = settings.OTEL_METRICS_IMPORT_URL
        if not base_url:
            self.stderr.write(self.style.ERROR("OTEL_METRICS_IMPORT_URL is not set."))
            return

        batch_size = options["batch_size"]
        if batch_size < 1:
            self.stderr.write(self.style.ERROR("--batch-size must be a positive integer."))
            return

        queryset = ProjectHealthMetrics.objects.select_related("project").order_by(
            "project_id", "nest_created_at"
        )
        if not options["all"]:
            latest = ProjectHealthMetrics.objects.aggregate(latest=Max("nest_created_at"))[
                "latest"
            ]
            if latest is None:
                self.stdout.write(self.style.WARNING("No project health metrics found."))
                return
            queryset = queryset.filter(nest_created_at__date=latest.date())

        # Group values and timestamps per metric/project series.
        series = defaultdict(lambda: {"values": [], "timestamps": []})
        for row in queryset.iterator():
            project_key = row.project.nest_key
            timestamp_ms = int(row.nest_created_at.timestamp() * 1000)
            for metric_name, field in METRIC_FIELDS.items():
                point = series[(metric_name, project_key)]
                point["values"].append(getattr(row, field))
                point["timestamps"].append(timestamp_ms)

        lines = [
            json.dumps(
                {
                    "metric": {"__name__": metric_name, "project": project_key},
                    "values": point["values"],
                    "timestamps": point["timestamps"],
                }
            )
            for (metric_name, project_key), point in series.items()
        ]

        import_url = f"{base_url.rstrip('/')}/api/v1/import"
        for start in range(0, len(lines), batch_size):
            payload = "\n".join(lines[start : start + batch_size])
            response = requests.post(import_url, data=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

        # VictoriaMetrics accepts the import without confirming storage (samples may be
        # dropped, e.g. outside the retention window), so verify the result in Grafana.
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {len(lines)} series to VictoriaMetrics. Verify they appear in Grafana."
            )
        )
