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
        # Try entity-based lookup first
        project_dtos = []

        for entity in entities[:3]:  # Limit entity lookups
            project_key = self._infer_project_key(entity)
            dto = self.project_service.get_project_details(project_key)
            if dto:
                project_dtos.append(dto)

        # Fall back to search if no direct matches
        if not project_dtos:
            project_dtos = self.project_service.search_projects(query, limit=5)

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
