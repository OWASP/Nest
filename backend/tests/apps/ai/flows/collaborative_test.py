"""Tests for collaborative flow."""

from unittest.mock import MagicMock, patch

from apps.ai.flows.collaborative import handle_collaborative_query


class TestHandleCollaborativeQuery:
    """Test cases for handle_collaborative_query."""

    @patch("apps.ai.common.utils.get_fallback_response")
    @patch("apps.ai.flows.collaborative.env")
    @patch("apps.ai.flows.collaborative.create_synthesizer_agent")
    @patch("apps.ai.flows.collaborative.get_intent_to_agent_map")
    @patch("apps.ai.flows.assistant.execute_task")
    def test_success_single_sub_query(
        self,
        mock_execute_task,
        mock_intent_map,
        mock_create_synthesizer,
        mock_env,
        mock_fallback,
    ):
        """Test successful flow with a single sub-query."""
        mock_agent = MagicMock()
        mock_intent_map.return_value = {"rag": lambda: mock_agent}

        mock_synthesizer = MagicMock()
        mock_create_synthesizer.return_value = mock_synthesizer

        mock_template = MagicMock()
        mock_template.render.return_value = "  synthesize this  "
        mock_env.get_template.return_value = mock_template

        mock_execute_task.side_effect = ["Expert response", "Synthesized response"]

        sub_queries = [{"intent": "rag", "query": "What is OWASP?"}]
        result = handle_collaborative_query("What is OWASP?", sub_queries)

        assert result == "Synthesized response"
        mock_env.get_template.assert_called_once_with("agents/synthesizer/tasks/synthesize.jinja")
        mock_template.render.assert_called_once_with(
            query="What is OWASP?",
            agent_responses=[("rag", "Expert response")],
        )

    @patch("apps.ai.flows.collaborative.env")
    @patch("apps.ai.flows.collaborative.create_synthesizer_agent")
    @patch("apps.ai.flows.collaborative.get_intent_to_agent_map")
    @patch("apps.ai.flows.assistant.execute_task")
    def test_success_multiple_sub_queries(
        self,
        mock_execute_task,
        mock_intent_map,
        mock_create_synthesizer,
        mock_env,
    ):
        """Test that each sub-query is dispatched to its own agent."""
        mock_rag_agent = MagicMock()
        mock_chapter_agent = MagicMock()
        mock_intent_map.return_value = {
            "rag": lambda: mock_rag_agent,
            "chapter": lambda: mock_chapter_agent,
        }

        mock_synthesizer = MagicMock()
        mock_create_synthesizer.return_value = mock_synthesizer

        mock_template = MagicMock()
        mock_template.render.return_value = "synthesize this"
        mock_env.get_template.return_value = mock_template

        mock_execute_task.side_effect = [
            "RAG response",
            "Chapter response",
            "Final synthesis",
        ]

        sub_queries = [
            {"intent": "rag", "query": "What is OWASP Top 10?"},
            {"intent": "chapter", "query": "Where is the London chapter?"},
        ]
        result = handle_collaborative_query("Tell me about OWASP", sub_queries)

        assert result == "Final synthesis"
        assert mock_execute_task.call_count == 3
        mock_template.render.assert_called_once_with(
            query="Tell me about OWASP",
            agent_responses=[
                ("rag", "RAG response"),
                ("chapter", "Chapter response"),
            ],
        )

    @patch("apps.ai.flows.collaborative.logger")
    @patch("apps.ai.flows.collaborative.env")
    @patch("apps.ai.flows.collaborative.create_synthesizer_agent")
    @patch("apps.ai.flows.collaborative.get_intent_to_agent_map")
    @patch("apps.ai.flows.assistant.execute_task")
    def test_unknown_intent_is_skipped_with_warning(
        self,
        mock_execute_task,
        mock_intent_map,
        mock_create_synthesizer,
        mock_env,
        mock_logger,
    ):
        """Test that sub-queries with unknown intents are skipped and a warning is logged."""
        mock_intent_map.return_value = {}

        mock_synthesizer = MagicMock()
        mock_create_synthesizer.return_value = mock_synthesizer

        mock_template = MagicMock()
        mock_template.render.return_value = "synthesize"
        mock_env.get_template.return_value = mock_template

        mock_execute_task.return_value = "Synthesized"

        sub_queries = [{"intent": "unknown_intent", "query": "Some query"}]
        handle_collaborative_query("Some query", sub_queries)

        mock_logger.warning.assert_called_once_with(
            "Unknown agent in collaborative flow: %s", "unknown_intent"
        )
        # execute_task should only be called once — for the synthesizer, not the sub-query
        mock_execute_task.assert_called_once()
        render_kwargs = mock_template.render.call_args[1]
        assert render_kwargs["agent_responses"] == []

    @patch("apps.ai.flows.collaborative.logger")
    @patch("apps.ai.flows.collaborative.env")
    @patch("apps.ai.flows.collaborative.create_synthesizer_agent")
    @patch("apps.ai.flows.collaborative.get_intent_to_agent_map")
    @patch("apps.ai.flows.assistant.execute_task")
    def test_mixed_known_and_unknown_intents(
        self,
        mock_execute_task,
        mock_intent_map,
        mock_create_synthesizer,
        mock_env,
        mock_logger,
    ):
        """Test that known intents are processed while unknown ones are skipped."""
        mock_agent = MagicMock()
        mock_intent_map.return_value = {"rag": lambda: mock_agent}

        mock_synthesizer = MagicMock()
        mock_create_synthesizer.return_value = mock_synthesizer

        mock_template = MagicMock()
        mock_template.render.return_value = "synthesize"
        mock_env.get_template.return_value = mock_template

        mock_execute_task.side_effect = ["RAG response", "Final synthesis"]

        sub_queries = [
            {"intent": "unknown_intent", "query": "Unknown query"},
            {"intent": "rag", "query": "Known query"},
        ]
        result = handle_collaborative_query("Mixed query", sub_queries)

        assert result == "Final synthesis"
        mock_logger.warning.assert_called_once_with(
            "Unknown agent in collaborative flow: %s", "unknown_intent"
        )
        render_kwargs = mock_template.render.call_args[1]
        assert render_kwargs["agent_responses"] == [("rag", "RAG response")]

    @patch("apps.ai.flows.collaborative.env")
    @patch("apps.ai.flows.collaborative.create_synthesizer_agent")
    @patch("apps.ai.flows.collaborative.get_intent_to_agent_map")
    @patch("apps.ai.flows.assistant.execute_task")
    def test_task_description_is_stripped(
        self,
        mock_execute_task,
        mock_intent_map,
        mock_create_synthesizer,
        mock_env,
    ):
        """Test that leading/trailing whitespace is stripped from the rendered template."""
        mock_agent = MagicMock()
        mock_intent_map.return_value = {"rag": lambda: mock_agent}
        mock_create_synthesizer.return_value = MagicMock()

        mock_template = MagicMock()
        mock_template.render.return_value = "  \n  task content  \n  "
        mock_env.get_template.return_value = mock_template

        mock_execute_task.side_effect = ["Expert response", "Final"]

        handle_collaborative_query("q", [{"intent": "rag", "query": "q"}])

        # The synthesizer execute_task call should receive the stripped description
        synthesizer_call = mock_execute_task.call_args_list[-1]
        assert synthesizer_call[1]["task_description"] == "task content"
