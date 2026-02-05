import openai
import pytest
from django.core.exceptions import ObjectDoesNotExist

from apps.ai.agent.nodes import AgentNodes
from apps.ai.common.constants import DEFAULT_CHUNKS_RETRIEVAL_LIMIT, DEFAULT_SIMILARITY_THRESHOLD


class TestAgentNodes:
    @pytest.fixture
    def mock_openai(self, mocker):
        mocker.patch("os.getenv", return_value="fake-key")
        return mocker.patch("apps.ai.agent.nodes.openai.OpenAI")

    @pytest.fixture
    def nodes(self, mock_openai, mocker):
        mocker.patch("apps.ai.agent.nodes.Retriever")
        mocker.patch("apps.ai.agent.nodes.Generator")
        return AgentNodes()

    def test_init_raises_error_without_api_key(self, mocker):
        mocker.patch("os.getenv", return_value=None)
        with pytest.raises(
            ValueError, match="DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
        ):
            AgentNodes()

    def test_retrieve_logic(self, nodes, mocker):
        state = {"query": "test query"}

        mock_metadata = {"entity_types": ["code"], "filters": {}, "requested_fields": []}
        nodes.extract_query_metadata = mocker.Mock(return_value=mock_metadata)

        nodes.retriever.retrieve.return_value = [{"text": "chunk1", "similarity": 0.9}]
        nodes.filter_chunks_by_metadata = mocker.Mock(
            return_value=[{"text": "chunk1", "similarity": 0.9}]
        )

        new_state = nodes.retrieve(state)

        assert "context_chunks" in new_state
        assert len(new_state["context_chunks"]) == 1
        assert new_state["extracted_metadata"] == mock_metadata

        nodes.retriever.retrieve.assert_called_with(
            query="test query",
            limit=DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
            similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
            content_types=["code"],
        )

    def test_retrieve_skips_if_chunks_present(self, nodes):
        state = {"context_chunks": ["existing"]}
        new_state = nodes.retrieve(state)
        assert new_state == state

    def test_generate_logic(self, nodes):
        state = {"query": "test query", "context_chunks": []}
        nodes.generator.generate_answer.return_value = "Generated answer"

        new_state = nodes.generate(state)

        assert new_state["answer"] == "Generated answer"
        assert new_state["iteration"] == 1
        assert len(new_state["history"]) == 1
        assert new_state["history"][0]["answer"] == "Generated answer"

    def test_evaluate_requires_more_context(self, nodes, mocker):
        state = {"query": "test", "answer": "unsure", "extracted_metadata": {}}

        mock_eval = {"requires_more_context": True, "feedback": "need more info"}
        nodes.call_evaluator = mocker.Mock(return_value=mock_eval)

        nodes.retriever.retrieve.return_value = ["new_chunk"]
        nodes.filter_chunks_by_metadata = mocker.Mock(return_value=["new_chunk"])

        new_state = nodes.evaluate(state)

        assert new_state["feedback"] == "Expand and refine answer using newly retrieved context."
        assert "context_chunks" in new_state
        assert new_state["evaluation"] == mock_eval

    def test_evaluate_updates_history(self, nodes, mocker):
        """Test that evaluation updates the last history entry."""
        state = {
            "query": "test",
            "answer": "good",
            "history": [{"iteration": 1, "answer": "good"}],
        }
        mock_eval = {"requires_more_context": False, "feedback": None, "complete": True}
        nodes.call_evaluator = mocker.Mock(return_value=mock_eval)

        new_state = nodes.evaluate(state)

        assert new_state["history"][-1]["evaluation"] == mock_eval

    def test_evaluate_complete(self, nodes, mocker):
        state = {"query": "test", "answer": "good"}
        mock_eval = {"requires_more_context": False, "feedback": None, "complete": True}
        nodes.call_evaluator = mocker.Mock(return_value=mock_eval)

        new_state = nodes.evaluate(state)
        assert new_state["feedback"] is None
        assert new_state["evaluation"] == mock_eval

    def test_route_from_evaluation(self, nodes):
        assert nodes.route_from_evaluation({"evaluation": {"complete": True}}) == "complete"
        assert (
            nodes.route_from_evaluation({"evaluation": {"complete": False}, "iteration": 0})
            == "refine"
        )
        assert (
            nodes.route_from_evaluation({"evaluation": {"complete": False}, "iteration": 100})
            == "complete"
        )

    def test_filter_chunks_by_metadata(self, nodes):
        chunks = [
            {"text": "foo", "additional_context": {"lang": "python"}, "similarity": 0.8},
            {"text": "bar", "additional_context": {"lang": "go"}, "similarity": 0.9},
        ]
        metadata = {"filters": {"lang": "python"}, "requested_fields": []}

        filtered = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert filtered[0]["text"] == "foo"

    def test_filter_chunks_empty_list(self, nodes):
        """Test filter_chunks_by_metadata returns empty list for empty input."""
        result = nodes.filter_chunks_by_metadata([], {"filters": {}}, limit=10)
        assert result == []

    def test_filter_chunks_no_filters(self, nodes):
        """Test filter_chunks_by_metadata returns original chunks when no filters."""
        chunks = [{"text": "chunk1", "similarity": 0.9}]
        metadata = {"filters": {}, "requested_fields": []}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result == chunks

    def test_filter_chunks_with_requested_fields(self, nodes):
        """Test filter_chunks_by_metadata scores chunks with requested fields."""
        chunks = [
            {"text": "no field", "additional_context": {}, "similarity": 0.8},
            {"text": "has field", "additional_context": {"name": "test"}, "similarity": 0.7},
        ]
        metadata = {"filters": {}, "requested_fields": ["name"]}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result[0]["text"] == "has field"

    def test_filter_chunks_with_list_metadata(self, nodes):
        """Test filter_chunks_by_metadata handles list metadata values."""
        chunks = [
            {
                "text": "has list",
                "additional_context": {"tags": ["python", "django"]},
                "similarity": 0.8,
            },
            {
                "text": "no match",
                "additional_context": {"tags": ["java", "spring"]},
                "similarity": 0.9,
            },
        ]
        metadata = {"filters": {"tags": "python"}, "requested_fields": []}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result[0]["text"] == "has list"

    def test_filter_chunks_exact_match(self, nodes):
        """Test filter_chunks_by_metadata handles exact non-string matches."""
        chunks = [
            {"text": "exact", "additional_context": {"count": 42}, "similarity": 0.8},
            {"text": "no match", "additional_context": {"count": 10}, "similarity": 0.9},
        ]
        metadata = {"filters": {"count": 42}, "requested_fields": []}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result[0]["text"] == "exact"

    def test_filter_chunks_content_match(self, nodes):
        """Test filter_chunks_by_metadata scores content matches."""
        chunks = [
            {"text": "contains python code", "additional_context": {}, "similarity": 0.7},
            {"text": "something else", "additional_context": {}, "similarity": 0.9},
        ]
        metadata = {"filters": {"lang": "python"}, "requested_fields": []}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result[0]["text"] == "contains python code"

    def test_filter_chunks_metadata_boost(self, nodes):
        """Test filter_chunks_by_metadata adds score for metadata richness."""
        chunks = [
            {"text": "rich", "additional_context": {"a": 1, "b": 2, "c": 3}, "similarity": 0.7},
            {"text": "poor", "additional_context": {}, "similarity": 0.9},
        ]
        metadata = {"filters": {"x": "y"}, "requested_fields": []}

        result = nodes.filter_chunks_by_metadata(chunks, metadata, limit=10)
        assert result[0]["text"] == "rich"

    def test_extract_query_metadata_openai_error(self, nodes, mocker):
        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_metadata_extractor_prompt", return_value="sys prompt"
        )
        nodes.openai_client.chat.completions.create.side_effect = openai.OpenAIError("Error")

        metadata = nodes.extract_query_metadata("query")
        assert metadata["intent"] == "general query"

    def test_extract_query_metadata_prompt_not_found(self, nodes, mocker):
        """Test extract_query_metadata raises when prompt not found."""
        mocker.patch("apps.ai.agent.nodes.Prompt.get_metadata_extractor_prompt", return_value=None)

        with pytest.raises(ObjectDoesNotExist, match="metadata-extractor-prompt"):
            nodes.extract_query_metadata("query")

    def test_extract_query_metadata_success(self, nodes, mocker):
        """Test successful metadata extraction from LLM."""
        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_metadata_extractor_prompt", return_value="sys prompt"
        )

        mock_response = mocker.Mock()
        mock_response.choices = [mocker.Mock()]
        mock_response.choices[
            0
        ].message.content = '{"entity_types": ["project"], "intent": "search"}'
        nodes.openai_client.chat.completions.create.return_value = mock_response

        metadata = nodes.extract_query_metadata("find OWASP projects")

        assert metadata["entity_types"] == ["project"]
        assert metadata["intent"] == "search"

    def test_call_evaluator_openai_error(self, nodes, mocker):
        nodes.generator.prepare_context.return_value = "ctx"
        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_evaluator_system_prompt", return_value="sys prompt"
        )
        nodes.openai_client.chat.completions.create.side_effect = openai.OpenAIError("Error")

        eval_result = nodes.call_evaluator(query="q", answer="a", context_chunks=[])
        assert eval_result["feedback"] == "Evaluator error or invalid response."

    def test_call_evaluator_prompt_not_found(self, nodes, mocker):
        """Test call_evaluator raises when prompt not found."""
        nodes.generator.prepare_context.return_value = "ctx"
        mocker.patch("apps.ai.agent.nodes.Prompt.get_evaluator_system_prompt", return_value=None)

        with pytest.raises(ObjectDoesNotExist, match="evaluator-system-prompt"):
            nodes.call_evaluator(query="q", answer="a", context_chunks=[])

    def test_call_evaluator_success(self, nodes, mocker):
        """Test successful evaluation from LLM."""
        nodes.generator.prepare_context.return_value = "ctx"
        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_evaluator_system_prompt", return_value="sys prompt"
        )

        mock_response = mocker.Mock()
        mock_response.choices = [mocker.Mock()]
        mock_response.choices[0].message.content = '{"complete": true, "feedback": null}'
        nodes.openai_client.chat.completions.create.return_value = mock_response

        eval_result = nodes.call_evaluator(query="q", answer="a", context_chunks=[])

        assert eval_result["complete"]
        assert eval_result["feedback"] is None
