import pytest

from apps.ai.agent.nodes import AgentNodes
from apps.ai.common.constants import DEFAULT_CHUNKS_RETRIEVAL_LIMIT, DEFAULT_SIMILARITY_THRESHOLD


class TestAgentNodes:
    @pytest.fixture
    def mock_openai(self, mocker):
        mocker.patch("os.getenv", return_value="fake-key")
        return mocker.patch("openai.OpenAI")

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

    def test_extract_query_metadata_openai_error(self, nodes, mocker):
        import openai

        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_metadata_extractor_prompt", return_value="sys prompt"
        )
        nodes.openai_client.chat.completions.create.side_effect = openai.OpenAIError("Error")

        metadata = nodes.extract_query_metadata("query")
        assert metadata["intent"] == "general query"

    def test_call_evaluator_openai_error(self, nodes, mocker):
        import openai

        nodes.generator.prepare_context.return_value = "ctx"
        mocker.patch(
            "apps.ai.agent.nodes.Prompt.get_evaluator_system_prompt", return_value="sys prompt"
        )
        nodes.openai_client.chat.completions.create.side_effect = openai.OpenAIError("Error")

        eval_result = nodes.call_evaluator(query="q", answer="a", context_chunks=[])
        assert eval_result["feedback"] == "Evaluator error or invalid response."
