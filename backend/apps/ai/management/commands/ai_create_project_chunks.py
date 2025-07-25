"""A command to create chunks of OWASP project data for RAG."""

import os

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Create chunks for OWASP project data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--project-key", type=str, help="Process only the project with this key"
        )
        parser.add_argument("--all", action="store_true", help="Process all the projects")
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of projects to process in each batch",
        )

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if options["project_key"]:
            queryset = Project.objects.filter(key=options["project_key"])
        elif options["all"]:
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(is_active=True)

        if not (total_projects := queryset.count()):
            self.stdout.write("No projects found to process")
            return

        self.stdout.write(f"Found {total_projects} projects to process")

        batch_size = options["batch_size"]
        for offset in range(0, total_projects, batch_size):
            batch_projects = queryset[offset : offset + batch_size]

            batch_chunks = []
            for project in batch_projects:
                chunks = self.create_chunks(project)
                batch_chunks.extend(chunks)

            if batch_chunks:
                chunks_count = len(batch_chunks)
                Chunk.bulk_save(batch_chunks)
                self.stdout.write(f"Saved {chunks_count} chunks")

        self.stdout.write(f"Completed processing all {total_projects} projects")

    def create_chunks(self, project: Project) -> list[Chunk]:
        prose_content, metadata_content = self.extract_project_content(project)

        all_chunk_texts = []

        if metadata_content.strip():
            all_chunk_texts.append(metadata_content)

        if prose_content.strip():
            prose_chunks = Chunk.split_text(prose_content)
            all_chunk_texts.extend(prose_chunks)

        if not all_chunk_texts:
            self.stdout.write(f"No content to chunk for project {project.key}")
            return []

        return create_chunks_and_embeddings(
            all_chunk_texts=all_chunk_texts,
            content_object=project,
            openai_client=self.openai_client,
        )

    def extract_project_content(self, project: Project) -> tuple[str, str]:
        prose_parts: list[str] = []
        metadata_parts: list[str] = []

        # Basic project information
        for value, label, target_list in [
            (project.name, "Project Name", metadata_parts),
            (project.description, "Description", prose_parts),
            (project.summary, "Summary", prose_parts),
            (project.level, "Project Level", metadata_parts),
            (project.type, "Project Type", metadata_parts),
        ]:
            if value:
                target_list.append(f"{label}: {value}")

        # Repository content
        repo = getattr(project, "owasp_repository", None)
        if repo:
            if repo.description:
                prose_parts.append(f"Repository Description: {repo.description}")
            if repo.topics:
                metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

        # Process all metadata fields in groups
        self._add_list_metadata(
            metadata_parts,
            [
                (project.languages, "Programming Languages"),
                (project.topics, "Topics"),
                (project.licenses, "Licenses"),
                (project.tags, "Tags"),
                (project.custom_tags, "Custom Tags"),
            ],
        )

        # Statistics
        stats_parts = [
            f"{label}: {count}"
            for count, label in [
                (project.stars_count, "Stars"),
                (project.forks_count, "Forks"),
                (project.contributors_count, "Contributors"),
                (project.releases_count, "Releases"),
                (project.open_issues_count, "Open Issues"),
            ]
            if count > 0
        ]
        if stats_parts:
            metadata_parts.append("Project Statistics: " + ", ".join(stats_parts))

        # Additional metadata and dates
        self._add_additional_metadata(metadata_parts, project)

        # Related URLs with validation
        if project.related_urls:
            valid_urls = [
                url
                for url in project.related_urls
                if url and url not in (project.invalid_urls or [])
            ]
            if valid_urls:
                metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

        return (
            DELIMITER.join(filter(None, prose_parts)),
            DELIMITER.join(filter(None, metadata_parts)),
        )

    def _add_list_metadata(self, metadata_parts, field_list):
        """Add list-based metadata fields."""
        for value_list, label in field_list:
            if value_list:
                metadata_parts.append(f"{label}: {', '.join(value_list)}")

    def _add_additional_metadata(self, metadata_parts, project):
        """Add additional metadata including dates and final fields."""
        # Leaders
        if project.leaders_raw:
            metadata_parts.append(f"Project Leaders: {', '.join(project.leaders_raw)}")

        # Date fields
        for date_value, label in [
            (project.created_at, "Created"),
            (project.updated_at, "Last Updated"),
            (project.released_at, "Last Release"),
        ]:
            if date_value:
                metadata_parts.append(f"{label}: {date_value.strftime('%Y-%m-%d')}")

        # Final metadata
        if project.health_score is not None:
            metadata_parts.append(f"Health Score: {project.health_score:.2f}")

        metadata_parts.extend(
            [
                f"Active Project: {'Yes' if project.is_active else 'No'}",
                f"Issue Tracking: {'Enabled' if project.track_issues else 'Disabled'}",
            ]
        )
