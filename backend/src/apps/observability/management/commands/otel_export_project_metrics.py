"""Export OWASP Nest project health metrics history to VictoriaMetrics.

`ProjectHealthMetrics` stores a daily snapshot per project (stars, forks,
contributors). This command copies the Nest project's history into
VictoriaMetrics using each row's date as the sample timestamp, so the metrics
show changes over time.

It writes directly to VictoriaMetrics' JSON import API rather than through the
OpenTelemetry pipeline, because OTel stamps every sample with the current time
and cannot represent historical values.

Modes:
  --all   export the full history (one-time backfill)
  default export only the latest snapshot day (for a daily run)
"""

import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max

from apps.owasp.models.project_health_metrics import ProjectHealthMetrics

NEST_PROJECT_KEY = "www-project-nest"
NEST_PROJECT_LABEL = "nest"

# VM metric name -> ProjectHealthMetrics field
METRIC_FIELDS = {
    "nest.project.stars": "stars_count",
    "nest.project.forks": "forks_count",
    "nest.project.contributors": "contributors_count",
}

REQUEST_TIMEOUT = 30


class Command(BaseCommand):
    help = "Export the Nest project health metrics history to VictoriaMetrics."

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

        metrics = ProjectHealthMetrics.objects.filter(project__key=NEST_PROJECT_KEY).order_by(
            "nest_created_at"
        )
        if not options["all"]:
            latest = metrics.aggregate(latest=Max("nest_created_at"))["latest"]
            if latest is None:
                self.stdout.write(self.style.WARNING("No Nest project health metrics found."))
                return
            metrics = metrics.filter(nest_created_at__date=latest.date())

        # Build one series per metric (the project is always Nest).
        series = {name: {"values": [], "timestamps": []} for name in METRIC_FIELDS}
        for row in metrics.iterator():
            timestamp_ms = int(row.nest_created_at.timestamp() * 1000)
            for metric_name, field in METRIC_FIELDS.items():
                series[metric_name]["values"].append(getattr(row, field))
                series[metric_name]["timestamps"].append(timestamp_ms)

        lines = [
            json.dumps(
                {
                    "metric": {"__name__": metric_name, "project": NEST_PROJECT_LABEL},
                    "values": point["values"],
                    "timestamps": point["timestamps"],
                }
            )
            for metric_name, point in series.items()
            if point["values"]
        ]
        if not lines:
            self.stdout.write(self.style.WARNING("No Nest project health metrics found."))
            return

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
