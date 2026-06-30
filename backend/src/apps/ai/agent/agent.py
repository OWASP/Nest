"""LangGraph-powered agent for iterative RAG answering."""

from __future__ import annotations

import logging
from typing import Any

from langgraph.graph import END, START, StateGraph

from apps.ai.agent.nodes import AgentNodes
from apps.ai.common.constants import (
    DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
    DEFAULT_SIMILARITY_THRESHOLD,
)

logger = logging.getLogger(__name__)


class AgenticRAGAgent:
    """LangGraph-based controller for agentic RAG with self-correcting retrieval."""

    def __init__(self) -> None:
        """Initialize the AgenticRAGAgent."""
        self.nodes = AgentNodes()
        self.graph = self.build_graph()

    def run(
        self,
        query: str,
    ) -> dict[str, Any]:
        """Execute the full RAG loop."""
        initial_state: dict[str, Any] = {
            "query": query,
            "iteration": 0,
            "feedback": None,
            "history": [],
            "content_types": [],
            "limit": DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
            "similarity_threshold": DEFAULT_SIMILARITY_THRESHOLD,
        }

        logger.info("Starting Agentic RAG workflow with metadata-aware retrieval")
        final_state = self.graph.invoke(initial_state)

        return {
            "answer": final_state.get("answer", ""),
            "iterations": final_state.get("iteration", 0),
            "evaluation": final_state.get("evaluation", {}),
            "context_chunks": final_state.get("context_chunks", []),
            "history": final_state.get("history", []),
            "extracted_metadata": final_state.get("extracted_metadata", {}),
        }

    def build_graph(self):
        """Build the LangGraph state machine for the RAG workflow."""
        graph = StateGraph(dict)
        graph.add_node("retrieve", self.nodes.retrieve)
        graph.add_node("generate", self.nodes.generate)
        graph.add_node("evaluate", self.nodes.evaluate)

        graph.add_edge(START, "retrieve")
        graph.add_edge("retrieve", "generate")
        graph.add_edge("generate", "evaluate")
        graph.add_conditional_edges(
            "evaluate",
            self.nodes.route_from_evaluation,
            {"refine": "generate", "complete": END},
        )

        return graph.compile()
