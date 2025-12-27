"""Intent-based query handler.

This module bridges Kabeer's IntentRouter (Layer 1) with the RAG pipeline.
STATIC intents get fast, cached responses. DYNAMIC intents trigger the
full retrieval-generation flow via the Engine.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from apps.ai.engine import Engine
from apps.ai.router import IntentRouter
from apps.core.services.project_service import ProjectPublicDTO, ProjectService

if TYPE_CHECKING:
    from typing import Any

logger = logging.getLogger(__name__)


class QueryHandler:
    """Handles user queries by routing to appropriate response strategy."""

    def __init__(self) -> None:
        """Initialize QueryHandler with router, service, and engine."""
        self.router = IntentRouter()
        self.project_service = ProjectService()
        self.engine = Engine()

    def handle(self, user_query: str) -> str:
        """Process a user query and return a response.

        Args:
            user_query: The user's natural language question.

        Returns:
            Generated response string.

        """
        intent_result = self.router.get_intent(user_query)
        intent_type = intent_result.get("intent", "DYNAMIC")

        logger.info("Query classified as %s: %s", intent_type, user_query[:50])

        if intent_type == "STATIC":
            return self._handle_static(intent_result)

        return self._handle_dynamic(intent_result)

    def _handle_static(self, intent_result: dict[str, Any]) -> str:
        """Handle STATIC intents with direct lookups.

        Args:
            intent_result: Router classification result.

        Returns:
            Response string for static query.

        """
        keyword = intent_result.get("args", {}).get("keyword", "")
        entities = intent_result.get("args", {}).get("entities", [])

        # Attempt project lookup if entities found
        if entities:
            project_key = self._infer_project_key(entities[0])
            project_dto = self.project_service.get_project_details(project_key)

            if project_dto:
                return self._format_static_response(project_dto, keyword)

        # Fallback to dynamic search
        return self._handle_dynamic(intent_result)

    def _handle_dynamic(self, intent_result: dict[str, Any]) -> str:
        """Handle DYNAMIC intents with RAG pipeline.

        Args:
            intent_result: Router classification result.

        Returns:
            LLM-generated response.

        """
        query = intent_result.get("args", {}).get("query", "")
        entities = intent_result.get("args", {}).get("entities", [])

        # Search for relevant projects
        project_dtos = self._retrieve_projects(query, entities)

        # Generate answer using sanitized DTOs only
        return self.engine.generate_answer(query, project_dtos)

    def _retrieve_projects(self, query: str, entities: list[str]) -> list[ProjectPublicDTO]:
        """Retrieve relevant projects for a query.

        Args:
            query: User's question.
            entities: Named entities extracted from query.

        Returns:
            List of sanitized project DTOs.

        """
        from apps.ai.models.chunk import Chunk
        from apps.ai.retriever import HybridRetriever

        # 1. Try entity-based lookup first
        project_dtos = []
        for entity in entities[:3]:
            project_key = self._infer_project_key(entity)
            if dto := self.project_service.get_project_details(project_key):
                project_dtos.append(dto)

        # 2. If we have good entity matches, we might stop here or mix them.
        # But for RAG, we often want the search context too.
        # However, if we found exact projects, maybe that's enough?
        # The spec says: "Call Retriever.search. Convert results... Call Engine."
        # It implies we ALWAYS search in dynamic flow. But let's keep entity matches if found.

        # 3. Hybrid Search
        retriever = HybridRetriever()
        search_results = retriever.search(query, limit=5)

        # 4. Convert chunks to Projects/Context
        # We need to map Chunk -> Context -> Entity -> Project
        # This is a bit complex. The Chunk has a context.
        # Let's gather the Chunk IDs and prefetch.
        chunk_ids = [r["source_id"] for r in search_results]
        chunks = Chunk.objects.filter(id__in=chunk_ids).select_related("context")

        seen_projects = {p.name for p in project_dtos}

        for chunk in chunks:
            # We assume the context entity IS a project or related to one.
            # For now, let's assume context.entity is a Project.
            # We need to handle GenericForeignKey.
            entity = chunk.context.entity

            # Check if it's a Project
            # Ideally we check isinstance(entity, Project) but let's use duck typing or class name
            if entity.__class__.__name__ == "Project" and entity.name not in seen_projects:
                # We need to convert this ORM model to DTO
                # We can reuse the service logic or map manually.
                # Reusing service is safer (sanitization).
                maintainer_names = []
                for leader in entity.entity_leaders:
                    name = getattr(leader, "name", None) or getattr(leader, "login", None)
                    if name:
                        maintainer_names.append(name)

                dto = ProjectPublicDTO(
                    name=entity.name or "",
                    url=entity.url,
                    description=entity.description,
                    maintainers=maintainer_names,
                )
                project_dtos.append(dto)
                seen_projects.add(entity.name)

        return project_dtos

    def _infer_project_key(self, entity: str) -> str:
        """Convert entity to project key format.

        Args:
            entity: Named entity from query.

        Returns:
            Formatted project key.

        """
        # Common OWASP project key format
        normalized = entity.lower().strip().replace(" ", "-")
        return f"www-project-{normalized}"

    def _format_static_response(self, project_dto: ProjectPublicDTO, keyword: str) -> str:
        """Format a static response for a project.

        Args:
            project_dto: Sanitized project data.
            keyword: Matched keyword from router.

        Returns:
            Formatted response string.

        """
        lines = [f"**{project_dto.name}**"]

        if project_dto.url:
            lines.append(f"URL: {project_dto.url}")

        if keyword in ("maintainer", "leader") and project_dto.maintainers:
            lines.append(f"Maintainers: {', '.join(project_dto.maintainers)}")
        elif project_dto.description:
            lines.append(project_dto.description)

        return "\n".join(lines)
