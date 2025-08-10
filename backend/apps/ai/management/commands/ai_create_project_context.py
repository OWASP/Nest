"""A command to update context for OWASP project data."""

from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_project_content
from apps.ai.common.utils import create_context
from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Update context for OWASP project data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--project-key",
            type=str,
            help="Process only the project with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the projects",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of projects to process in each batch",
        )

    def handle(self, *args, **options):
        if options["project_key"]:
            queryset = Project.objects.filter(key=options["project_key"])
        elif options["all"]:
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(is_active=True)
        queryset = queryset.order_by("id")

        if not (total_projects := queryset.count()):
            self.stdout.write("No projects found to process")
            return

        self.stdout.write(f"Found {total_projects} projects to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_projects, batch_size):
            batch_projects = queryset[offset : offset + batch_size]
            processed_count += self.process_context_batch(batch_projects)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_projects} projects")
        )

    def process_context_batch(self, projects: list[Project]) -> int:
        """Process a batch of projects to create contexts."""
        processed = 0

        for project in projects:
            prose_content, metadata_content = extract_project_content(project)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content for project {project.key}")
                continue

            if create_context(
                content=full_content, content_object=project, source="owasp_project"
            ):
                processed += 1
                self.stdout.write(f"Created context for {project.key}")
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create context for {project.key}"))
        return processed
