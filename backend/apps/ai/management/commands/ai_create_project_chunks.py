"""A command to create chunks of OWASP project data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings, create_context
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
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
        parser.add_argument(
            "--context",
            action="store_true",
            help="Create only context (skip chunks and embeddings)",
        )
        parser.add_argument(
            "--chunks",
            action="store_true",
            help="Create only chunks+embeddings (requires existing context)",
        )

    def handle(self, *args, **options):
        if not options["context"] and not options["chunks"]:
            self.stdout.write(self.style.ERROR("Must specify either --context or --chunks"))
            return

        if options["chunks"] and not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        if options["chunks"]:
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
        processed_count = 0

        for offset in range(0, total_projects, batch_size):
            batch_projects = queryset[offset : offset + batch_size]

            if options["context"]:
                processed_count += self.process_context_batch(batch_projects)
            elif options["chunks"]:
                processed_count += self.process_chunks_batch(batch_projects)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_projects} projects")
        )

    def process_context_batch(self, projects: list[Project]) -> int:
        """Process a batch of projects to create contexts."""
        processed = 0

        for project in projects:
            prose_content, metadata_content = self.extract_project_content(project)
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

    def process_chunks_batch(self, projects: list[Project]) -> int:
        """Process a batch of projects to create chunks."""
        processed = 0
        batch_chunks = []

        project_content_type = ContentType.objects.get_for_model(Project)

        for project in projects:
            context = Context.objects.filter(
                content_type=project_content_type, object_id=project.id
            ).first()

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for project {project.key}")
                )
                continue

            prose_content, metadata_content = self.extract_project_content(project)
            all_chunk_texts = []

            if metadata_content.strip():
                all_chunk_texts.append(metadata_content)

            if prose_content.strip():
                prose_chunks = Chunk.split_text(prose_content)
                all_chunk_texts.extend(prose_chunks)

            if not all_chunk_texts:
                self.stdout.write(f"No content to chunk for project {project.key}")
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=all_chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(f"Created {len(chunks)} chunks for {project.key}")

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)
        return processed

    def extract_project_content(self, project: Project) -> tuple[str, str]:
        prose_parts = []
        metadata_parts = []

        if project.name:
            metadata_parts.append(f"Project Name: {project.name}")

        if project.description:
            prose_parts.append(f"Description: {project.description}")

        if project.summary:
            prose_parts.append(f"Summary: {project.summary}")

        if project.level:
            metadata_parts.append(f"Project Level: {project.level}")

        if project.type:
            metadata_parts.append(f"Project Type: {project.type}")

        if hasattr(project, "owasp_repository") and project.owasp_repository:
            repo = project.owasp_repository
            if repo.description:
                prose_parts.append(f"Repository Description: {repo.description}")
            if repo.topics:
                metadata_parts.append(f"Repository Topics: {', '.join(repo.topics)}")

        if project.languages:
            metadata_parts.append(f"Programming Languages: {', '.join(project.languages)}")

        if project.topics:
            metadata_parts.append(f"Topics: {', '.join(project.topics)}")

        if project.licenses:
            metadata_parts.append(f"Licenses: {', '.join(project.licenses)}")

        if project.tags:
            metadata_parts.append(f"Tags: {', '.join(project.tags)}")

        if project.custom_tags:
            metadata_parts.append(f"Custom Tags: {', '.join(project.custom_tags)}")

        stats_parts = []
        if project.stars_count > 0:
            stats_parts.append(f"Stars: {project.stars_count}")
        if project.forks_count > 0:
            stats_parts.append(f"Forks: {project.forks_count}")
        if project.contributors_count > 0:
            stats_parts.append(f"Contributors: {project.contributors_count}")
        if project.releases_count > 0:
            stats_parts.append(f"Releases: {project.releases_count}")
        if project.open_issues_count > 0:
            stats_parts.append(f"Open Issues: {project.open_issues_count}")

        if stats_parts:
            metadata_parts.append("Project Statistics: " + ", ".join(stats_parts))

        if project.leaders_raw:
            metadata_parts.append(f"Project Leaders: {', '.join(project.leaders_raw)}")

        if project.related_urls:
            valid_urls = [
                url
                for url in project.related_urls
                if url and url not in (project.invalid_urls or [])
            ]
            if valid_urls:
                metadata_parts.append(f"Related URLs: {', '.join(valid_urls)}")

        if project.created_at:
            metadata_parts.append(f"Created: {project.created_at.strftime('%Y-%m-%d')}")

        if project.updated_at:
            metadata_parts.append(f"Last Updated: {project.updated_at.strftime('%Y-%m-%d')}")

        if project.released_at:
            metadata_parts.append(f"Last Release: {project.released_at.strftime('%Y-%m-%d')}")

        if project.health_score is not None:
            metadata_parts.append(f"Health Score: {project.health_score:.2f}")

        metadata_parts.append(f"Active Project: {'Yes' if project.is_active else 'No'}")

        metadata_parts.append(
            f"Issue Tracking: {'Enabled' if project.track_issues else 'Disabled'}"
        )

        return (
            DELIMITER.join(filter(None, prose_parts)),
            DELIMITER.join(filter(None, metadata_parts)),
        )
