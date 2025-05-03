"""A command to add project custom tags."""

import json
from argparse import ArgumentParser
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Add custom tags to OWASP projects."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-line arguments to the parser.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "file-name",
            type=str,
            help="The name of the file containing custom tags. "
            "The file should be placed in the data/project-custom-tags directory."
            "Example: gsoc-2024.json",
        )

    def handle(self, *_args, **options) -> None:
        """Handle the command execution."""
        file_path = Path(settings.BASE_DIR / f"data/project-custom-tags/{options['file-name']}")
        if not file_path.exists():
            self.stderr.write(f"File not found: {file_path}")
            return

        with Path.open(file_path) as file:
            file_contents = json.load(file)
            projects = file_contents["projects"]
            tags = file_contents["tags"]

        if not projects or not tags:
            self.stderr.write("No projects or tags found in the file.")
            return

        for project_key in projects:
            try:
                project = Project.objects.get(key=project_key)
            except Project.DoesNotExist:
                self.stderr.write(f"Project {project_key} does not exists.")
                continue

            project.custom_tags = sorted(set(project.custom_tags + tags))
            project.save(update_fields=["custom_tags"])
