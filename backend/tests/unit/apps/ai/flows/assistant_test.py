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


@patch("apps.ai.flows.assistant.analyze_query")
@patch("apps.ai.flows.assistant.create_clarification_agent")
@patch("apps.ai.flows.assistant.route")
@patch("apps.ai.flows.assistant.execute_task")
def test_low_confidence_non_rag_triggers_clarification(
    mock_execute_task, mock_route, mock_create_clarify, mock_analyze_query
):
    """Low-confidence non-RAG routing should call Clarification Agent."""
    mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
    mock_route.return_value = {"intent": "project", "confidence": 0.5}
    clarification_agent = MagicMock(name="clarification_agent")
    mock_create_clarify.return_value = clarification_agent
    mock_execute_task.return_value = "Clarify: which project?"

    res = process_query("Ambiguous query", is_app_mention=True)

    mock_create_clarify.assert_called_once()
    mock_execute_task.assert_called_once_with(clarification_agent, "Ambiguous query")
    assert res == "Clarify: which project?"


@patch("apps.ai.flows.assistant.analyze_query")
@patch("apps.ai.flows.assistant.create_clarification_agent")
@patch("apps.ai.flows.assistant.route")
@patch("apps.ai.flows.assistant.execute_task")
def test_low_confidence_rag_triggers_clarification_when_policy_removed(
    mock_execute_task, mock_route, mock_create_clarify, mock_analyze_query
):
    """Low-confidence RAG routing should also call Clarification Agent."""
    mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
    mock_route.return_value = {"intent": "rag", "confidence": 0.4}
    clarification_agent = MagicMock(name="clarification_agent")
    mock_create_clarify.return_value = clarification_agent
    mock_execute_task.return_value = "Clarify: please specify 'this'"

    res = process_query("Is this covered by OWASP?", is_app_mention=True)

    mock_create_clarify.assert_called_once()
    mock_execute_task.assert_called_once_with(clarification_agent, "Is this covered by OWASP?")
    assert res == "Clarify: please specify 'this'"


class TestCache:
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_cache_hit_returns_early(self, mock_get_cached):
        """Semantic cache hit should return cached response without routing."""
        mock_get_cached.return_value = "cached answer"

        result = process_query("What is OWASP?")

        assert result == "cached answer"
        mock_get_cached.assert_called_once_with("What is OWASP?")

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_cache_miss_proceeds_to_routing(
        self, mock_get_cached, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Cache miss should proceed with normal routing."""
        mock_get_cached.return_value = None
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "agent response"

        result = process_query("What is OWASP?")

        assert result == "agent response"
        mock_get_cached.assert_called_once()
        mock_route.assert_called_once()

    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_cache_lookup_exception_proceeds_normally(
        self, mock_get_cached, mock_execute_task, mock_route, mock_analyze_query
    ):
        """Cache lookup failure should log and proceed without crashing."""
        mock_get_cached.side_effect = Exception("Redis down")
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "agent response"

        result = process_query("What is OWASP?")

        assert result == "agent response"

    @patch("apps.ai.flows.assistant.store_cached_response")
    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_response_stored_in_cache_after_execution(
        self,
        mock_get_cached,
        mock_execute_task,
        mock_route,
        mock_analyze_query,
        mock_store_cached,
    ):
        """Successful agent response should be stored in semantic cache."""
        mock_get_cached.return_value = None
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "agent response"

        process_query("What is OWASP?")

        mock_store_cached.assert_called_once_with(
            query="What is OWASP?",
            response="agent response",
            intent="rag",
            confidence=0.9,
        )

    @patch("apps.ai.flows.assistant.store_cached_response")
    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.route")
    @patch("apps.ai.flows.assistant.execute_task")
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_cache_store_failure_still_returns_response(
        self,
        mock_get_cached,
        mock_execute_task,
        mock_route,
        mock_analyze_query,
        mock_store_cached,
    ):
        """Cache store exception must not prevent response from being returned."""
        mock_get_cached.return_value = None
        mock_analyze_query.return_value = {"is_simple": True, "sub_queries": []}
        mock_route.return_value = {"intent": "rag", "confidence": 0.9}
        mock_execute_task.return_value = "agent response"
        mock_store_cached.side_effect = Exception("DB write failed")

        result = process_query("What is OWASP?")

        assert result == "agent response"

    @patch("apps.ai.flows.assistant.store_cached_response")
    @patch("apps.ai.flows.assistant.handle_collaborative_query")
    @patch("apps.ai.flows.assistant.analyze_query")
    @patch("apps.ai.flows.assistant.get_cached_response")
    def test_collaborative_flow_stores_in_cache(
        self,
        mock_get_cached,
        mock_analyze_query,
        mock_collab,
        mock_store_cached,
    ):
        """Collaborative flow response should be stored in cache."""
        mock_get_cached.return_value = None
        mock_analyze_query.return_value = {
            "is_simple": False,
            "sub_queries": ["sub1", "sub2"],
        }
        mock_collab.return_value = "collaborative response"

        result = process_query("Complex multi-part question")

        assert result == "collaborative response"
        mock_store_cached.assert_called_once_with(
            query="Complex multi-part question",
            response="collaborative response",
        )
