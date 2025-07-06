"""A command to create chunks of OWASP project data for RAG."""

import os
import time
from datetime import UTC, datetime, timedelta

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    DELIMITER,
    MIN_REQUEST_INTERVAL_SECONDS,
)
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

        try:
            time_since_last_request = datetime.now(UTC) - getattr(
                self,
                "last_request_time",
                datetime.now(UTC) - timedelta(seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS),
            )

            if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
                time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

            response = self.openai_client.embeddings.create(
                input=all_chunk_texts,
                model="text-embedding-3-small",
            )
            self.last_request_time = datetime.now(UTC)

            return [
                chunk
                for text, embedding in zip(
                    all_chunk_texts,
                    [d.embedding for d in response.data],
                    strict=True,
                )
                if (
                    chunk := Chunk.update_data(
                        text=text,
                        content_object=project,
                        embedding=embedding,
                        save=False,
                    )
                )
            ]
        except openai.OpenAIError as e:
            self.stdout.write(self.style.ERROR(f"OpenAI API error for project {project.key}: {e}"))
            return []

    def extract_project_content(self, project: Project) -> tuple[str, str]:
        prose_parts = []
        metadata_parts = []

        if project.name:
            metadata_parts.append(f"Project Name: {project.name}")

        if project.description :
            prose_parts.append(f"Description: {project.description}")

        if project.summary:
            prose_parts.append(f"Summary: {project.summary}")

        if project.level:
            metadata_parts.append(f"Project Level: {project.level}")

        if project.type:
            metadata_parts.append(f"Project Type: {project.type}")

        if hasattr(project, "owasp_repository") and project.owasp_repository:
            repo = project.owasp_repository
            if repo.description :
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
            leaders_info = []
            for leader in project.leaders_raw:
                if isinstance(leader, dict):
                    leader_name = leader.get("name", "")
                    leader_email = leader.get("email", "")
                    if leader_name:
                        leader_text = f"Leader: {leader_name}"
                        if leader_email:
                            leader_text += f" ({leader_email})"
                        leaders_info.append(leader_text)

            if leaders_info:
                metadata_parts.append("Project Leaders: " + ", ".join(leaders_info))

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
