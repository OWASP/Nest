"""Tests for assistant flow image context enrichment."""

from unittest.mock import MagicMock, patch

from apps.ai.flows.assistant import process_query


class TestProcessQueryImageEnrichment:
    """Test cases for image context enrichment in process_query."""

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.OpenAi")
    def test_process_query_with_images_enriches_query(
        self, mock_openai_cls, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Test that images trigger OpenAI vision call and enrich the query."""
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_openai_instance = MagicMock()
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_images.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = "A screenshot of a login page"
        mock_openai_cls.return_value = mock_openai_instance

        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "Response"

        images = ["data:image/png;base64,abc123"]

        process_query("What is this?", images=images)

        mock_openai_instance.set_images.assert_called_once_with(images)
        mock_openai_instance.complete.assert_called_once()

        # Verify the enriched query is passed to route
        enriched_query = mock_route.call_args[0][0]
        assert "Image context: A screenshot of a login page" in enriched_query
        assert "What is this?" in enriched_query

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.OpenAi")
    def test_process_query_with_images_vision_failure(
        self, mock_openai_cls, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Test that failed vision call proceeds with original query."""
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_openai_instance = MagicMock()
        mock_openai_instance.set_prompt.return_value = mock_openai_instance
        mock_openai_instance.set_input.return_value = mock_openai_instance
        mock_openai_instance.set_images.return_value = mock_openai_instance
        mock_openai_instance.complete.return_value = None
        mock_openai_cls.return_value = mock_openai_instance

        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "Response"

        process_query("What is this?", images=["data:image/png;base64,abc"])

        # Original query should be passed without enrichment
        enriched_query = mock_route.call_args[0][0]
        assert enriched_query == "What is this?"
        assert "Image context" not in enriched_query

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.OpenAi")
    def test_process_query_without_images_skips_vision(
        self, mock_openai_cls, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Test that no images means no vision API call."""
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "Response"

        process_query("What is OWASP?")

        mock_openai_cls.assert_not_called()

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.OpenAi")
    def test_process_query_empty_images_skips_vision(
        self, mock_openai_cls, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Test that empty images list means no vision API call."""
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "Response"

        process_query("What is OWASP?", images=[])

        mock_openai_cls.assert_not_called()


@patch("apps.ai.flows.assistant.create_clarification_agent")
@patch("apps.ai.flows.assistant.route")
@patch("apps.ai.flows.assistant.execute_task")
def test_low_confidence_non_rag_triggers_clarification(
    mock_execute_task, mock_route, mock_create_clarify
):
    """Low-confidence non-RAG routing should call Clarification Agent."""
    mock_route.return_value = {"intent": "project", "confidence": 0.5}
    clarification_agent = MagicMock(name="clarification_agent")
    mock_create_clarify.return_value = clarification_agent
    mock_execute_task.return_value = "Clarify: which project?"

    res = process_query("Ambiguous query", is_app_mention=True)

    mock_create_clarify.assert_called_once()
    mock_execute_task.assert_called_once_with(clarification_agent, "Ambiguous query")
    assert res == "Clarify: which project?"


@patch("apps.ai.flows.assistant.create_clarification_agent")
@patch("apps.ai.flows.assistant.route")
@patch("apps.ai.flows.assistant.execute_task")
def test_low_confidence_rag_triggers_clarification_when_policy_removed(
    mock_execute_task, mock_route, mock_create_clarify
):
    """Low-confidence RAG routing should also call Clarification Agent."""
    mock_route.return_value = {"intent": "rag", "confidence": 0.4}
    clarification_agent = MagicMock(name="clarification_agent")
    mock_create_clarify.return_value = clarification_agent
    mock_execute_task.return_value = "Clarify: please specify 'this'"

    res = process_query("Is this covered by OWASP?", is_app_mention=True)

    mock_create_clarify.assert_called_once()
    mock_execute_task.assert_called_once_with(clarification_agent, "Is this covered by OWASP?")
    assert res == "Clarify: please specify 'this'"
