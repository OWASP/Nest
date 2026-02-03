"""A command to generate backend model graphs for CI."""

from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Generate per-app and inter-app model graphs."""

    help = "Generate per-app and inter-app model graphs"

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR) / "model-graphs"
        apps_dir = base_dir / "apps"
        inter_dir = base_dir / "inter-app"

        apps_dir.mkdir(parents=True, exist_ok=True)
        inter_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Collecting app labels...")

        app_labels = [
            app.label
            for app in apps.get_app_configs()
            if not app.name.startswith("django.")
            and not app.name.startswith("django.contrib.")
            and app.label != "django_extensions"
        ]

        failures: list[str] = []

        for label in app_labels:
            self.stdout.write(f"Generating graphs for {label}")

            try:
                call_command(
                    "graph_models",
                    label,
                    "--inheritance",
                    output=str(apps_dir / f"{label}_inheritance.svg"),
                )
            except (CommandError, OSError) as exc:
                self.stderr.write(f"[warn] inheritance graph failed for {label}: {exc}")
                failures.append(f"{label} inheritance")

            try:
                call_command(
                    "graph_models",
                    label,
                    "--no-inheritance",
                    output=str(apps_dir / f"{label}_relations.svg"),
                )
            except (CommandError, OSError) as exc:
                self.stderr.write(f"[warn] relations graph failed for {label}: {exc}")
                failures.append(f"{label} relations")

        self.stdout.write("Generating inter-app graphs")

        try:
            call_command(
                "graph_models",
                "--all-applications",
                "--inheritance",
                output=str(inter_dir / "backend_inheritance.svg"),
            )
        except (CommandError, OSError) as exc:
            self.stderr.write(f"[warn] inter inheritance failed: {exc}")
            failures.append("inter-app inheritance")

        try:
            call_command(
                "graph_models",
                "--all-applications",
                "--no-inheritance",
                output=str(inter_dir / "backend_relations.svg"),
            )
        except (CommandError, OSError) as exc:
            self.stderr.write(f"[warn] inter relations failed: {exc}")
            failures.append("inter-app relations")

        if failures:
            self.stdout.write(
                self.style.WARNING(
                    "Model graph generation completed with failures: " + ", ".join(failures)
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Model graph generation completed"))
