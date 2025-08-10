"""A command to create chunks of OWASP project data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_project_content
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.owasp.models.project import Project


class Command(BaseCommand):
    help = "Create chunks for OWASP project data"

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
        processed_count = 0

        for offset in range(0, total_projects, batch_size):
            batch_projects = queryset[offset : offset + batch_size]
            processed_count += self.process_chunks_batch(batch_projects)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_projects} projects")
        )

    def process_chunks_batch(self, projects: list[Project]) -> int:
        """Process a batch of projects to create chunks."""
        processed = 0
        batch_chunks = []

        project_content_type = ContentType.objects.get_for_model(Project)
        project_ids = [p.id for p in projects]
        contexts_by_id = {
            c.object_id: c
            for c in Context.objects.filter(
                content_type=project_content_type, object_id__in=project_ids
            )
        }

        for project in projects:
            context = contexts_by_id.get(project.id)

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for project {project.key}")
                )
                continue

            prose_content, metadata_content = extract_project_content(project)
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
