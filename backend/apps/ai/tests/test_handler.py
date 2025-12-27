from unittest.mock import patch

from apps.ai.handler import QueryHandler
from apps.core.services.project_service import ProjectPublicDTO


def test_handler_static_flow():
    """Verify STATIC intent triggers project service."""
    with (
        patch("apps.ai.handler.IntentRouter") as mock_router,
        patch("apps.ai.handler.ProjectService") as mock_service,
        patch("apps.ai.handler.Engine") as mock_engine,
    ):
        # Setup mocks
        router_instance = mock_router.return_value
        router_instance.get_intent.return_value = {
            "intent": "STATIC",
            "args": {"keyword": "maintainer", "entities": ["Zap"]},
        }

        service_instance = mock_service.return_value
        service_instance.get_project_details.return_value = ProjectPublicDTO(
            name="OWASP Zap", url="http://zap.org", description="Scanner", maintainers=["Simon"]
        )

        # Test
        handler = QueryHandler()
        response = handler.handle("Who runs Zap?")

        # Verify
        service_instance.get_project_details.assert_called()
        # Static flow should NOT invoke LLM
        mock_engine.return_value.generate_answer.assert_not_called()
        assert "OWASP Zap" in response
        assert "Simon" in response


def test_handler_dynamic_flow():
    """Verify DYNAMIC intent triggers Retriever and Engine."""
    with (
        patch("apps.ai.handler.IntentRouter") as mock_router,
        patch("apps.ai.handler.HybridRetriever") as mock_retriever,
        patch("apps.ai.handler.Engine") as mock_engine,
        patch("apps.ai.handler.ProjectService"),
    ):  # Mock service to avoid side effects
        # Setup
        router_instance = mock_router.return_value
        router_instance.get_intent.return_value = {
            "intent": "DYNAMIC",
            "args": {"query": "How to secure API?", "entities": []},
        }

        retriever_instance = mock_retriever.return_value
        retriever_instance.search.return_value = [{"source_id": 1, "text": "chunk1", "score": 0.5}]

        engine_instance = mock_engine.return_value
        engine_instance.generate_answer.return_value = "Secure APIs by..."

        # We also need to mock Chunk lookup in _retrieve_projects
        # This is tricky because it does Chunk.objects.filter...
        # Ideally we mock the whole _retrieve_projects method or DB access.
        # For unit test simplicity, let's mock _retrieve_projects directly

        with patch.object(QueryHandler, "_retrieve_projects", return_value=[]) as mock_retrieve:
            handler = QueryHandler()
            response = handler.handle("How to secure API?")

            mock_retrieve.assert_called_with("How to secure API?", [])
            engine_instance.generate_answer.assert_called()
            assert response == "Secure APIs by..."
