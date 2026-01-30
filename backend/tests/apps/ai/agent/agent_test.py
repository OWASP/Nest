"""Tests for the AgenticRAGAgent class."""

from unittest.mock import MagicMock

from apps.ai.agent.agent import AgenticRAGAgent


class TestAgenticRAGAgent:
    """Tests for AgenticRAGAgent."""

    target_module = "apps.ai.agent.agent"

    def test_init(self, mocker):
        """Test AgenticRAGAgent initialization."""
        mock_nodes = mocker.patch(f"{self.target_module}.AgentNodes")
        mock_state_graph = mocker.patch(f"{self.target_module}.StateGraph")

        mock_graph_instance = MagicMock()
        mock_state_graph.return_value = mock_graph_instance

        agent = AgenticRAGAgent()

        mock_nodes.assert_called_once()
        assert agent.nodes is not None
        assert agent.graph is not None

    def test_run(self, mocker):
        """Test the run method executes the RAG workflow."""
        mocker.patch(f"{self.target_module}.AgentNodes")
        mock_state_graph = mocker.patch(f"{self.target_module}.StateGraph")

        mock_graph_instance = MagicMock()
        mock_compiled_graph = MagicMock()
        mock_state_graph.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = mock_compiled_graph

        mock_compiled_graph.invoke.return_value = {
            "answer": "Test answer",
            "iteration": 2,
            "evaluation": {"score": 0.9},
            "context_chunks": [{"text": "chunk1"}],
            "history": ["step1", "step2"],
            "extracted_metadata": {"key": "value"},
        }

        agent = AgenticRAGAgent()
        result = agent.run("Test query")

        mock_compiled_graph.invoke.assert_called_once()
        assert result["answer"] == "Test answer"
        assert result["iterations"] == 2
        assert result["evaluation"] == {"score": 0.9}
        assert result["context_chunks"] == [{"text": "chunk1"}]
        assert result["history"] == ["step1", "step2"]
        assert result["extracted_metadata"] == {"key": "value"}

    def test_run_with_empty_result(self, mocker):
        """Test run method handles empty results gracefully."""
        mocker.patch(f"{self.target_module}.AgentNodes")
        mock_state_graph = mocker.patch(f"{self.target_module}.StateGraph")

        mock_graph_instance = MagicMock()
        mock_compiled_graph = MagicMock()
        mock_state_graph.return_value = mock_graph_instance
        mock_graph_instance.compile.return_value = mock_compiled_graph

        mock_compiled_graph.invoke.return_value = {}

        agent = AgenticRAGAgent()
        result = agent.run("Test query")

        assert result["answer"] == ""
        assert result["iterations"] == 0
        assert result["evaluation"] == {}
        assert result["context_chunks"] == []
        assert result["history"] == []
        assert result["extracted_metadata"] == {}

    def test_build_graph(self, mocker):
        """Test build_graph creates the correct state machine."""
        mocker.patch(f"{self.target_module}.AgentNodes")
        mock_state_graph = mocker.patch(f"{self.target_module}.StateGraph")
        mock_start = mocker.patch(f"{self.target_module}.START")
        mocker.patch(f"{self.target_module}.END")

        mock_graph_instance = MagicMock()
        mock_state_graph.return_value = mock_graph_instance

        AgenticRAGAgent()

        assert mock_graph_instance.add_node.call_count == 3
        mock_graph_instance.add_edge.assert_any_call(mock_start, "retrieve")
        mock_graph_instance.add_edge.assert_any_call("retrieve", "generate")
        mock_graph_instance.add_edge.assert_any_call("generate", "evaluate")
        mock_graph_instance.add_conditional_edges.assert_called_once()
        mock_graph_instance.compile.assert_called_once()
