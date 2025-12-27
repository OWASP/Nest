"""Layer 2 Handler for deterministic static lookups."""

import logging

from asgiref.sync import sync_to_async

from apps.ai.core.dtos import AIResponseDTO, ProjectPublicDTO, RouterIntentDTO
from apps.github.models.repository import Repository

logger = logging.getLogger(__name__)


class StaticService:
    """Handles deterministic lookups against the local database."""

    async def execute(self, text: str, confidence: float) -> AIResponseDTO | None:
        """Execute the static lookup logic."""
        project = await self._find_repo_by_name(text)
        if not project:
            return None

        # Sanitize data using DTO
        safe_data = ProjectPublicDTO(
            name=project.name,
            description=project.description,
            url=project.url,
            stars=project.stargazers_count,
        )

        return AIResponseDTO(
            answer=f"Found Project: {safe_data.name}. {safe_data.description}",
            source="database",
            intent=RouterIntentDTO(label="STATIC", confidence=confidence),
        )

    @sync_to_async
    def _find_repo_by_name(self, name: str):
        """Run the actual DB query synchronously in a thread-safe way."""
        return Repository.objects.filter(name__icontains=name).first()
