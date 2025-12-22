"""Integration tests for ProjectService Layer 2 and Layer 3 logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from apps.ai.core.dtos import AIQueryDTO, AIResponseDTO, RouterIntentDTO
from apps.ai.core.services.project_service import ProjectService


@pytest.mark.asyncio
class TestProjectService:
    """Test suite for validating the AI Service Layer orchestration."""

    async def test_process_query_static_success(self):
        """Verify Layer 2: Deterministic DB lookup when intent is 'static'."""
        service = ProjectService()
        query = AIQueryDTO(text="Tell me about project nest")

        # Mock Router return (Exact match to your intent.py output)
        service.router.get_intent = MagicMock(
            return_value={
                "intent": "STATIC",
                "confidence": 1.0,
                "source": "spacy_heuristic",
                "args": {},
            }
        )

        # Mock Static Service return
        mock_res = AIResponseDTO(
            answer="Project Nest is an OWASP tool.",
            source="database",
            intent=RouterIntentDTO(label="STATIC", confidence=1.0),
        )
        service.static_service.execute = AsyncMock(return_value=mock_res)

        result = await service.process_query(query)

        assert result.source == "database"
        assert "OWASP tool" in result.answer

    async def test_process_query_hybrid_fallback(self):
        """Verify Layer 3: Fallback to Hybrid RAG when DB returns no match."""
        service = ProjectService()
        query = AIQueryDTO(text="Explain security")

        # Mock Router return
        service.router.get_intent = MagicMock(
            return_value={"intent": "STATIC", "confidence": 0.80}
        )

        # Mock Static Service failure (None)
        service.static_service.execute = AsyncMock(return_value=None)

        result = await service.process_query(query)

        assert result.source == "hybrid_rag"
        assert result.show_manual_search_btn is True
