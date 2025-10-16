"""LangGraph nodes for the Agentic RAG workflow."""

from __future__ import annotations

import json
import os
from typing import Any

import openai
from django.core.exceptions import ObjectDoesNotExist

from apps.ai.agent.tools.rag.generator import Generator
from apps.ai.agent.tools.rag.retriever import Retriever
from apps.ai.common.constants import (
    DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_REASONING_MODEL,
    DEFAULT_SIMILARITY_THRESHOLD,
)
from apps.ai.common.utils import extract_json_from_markdown
from apps.core.models.prompt import Prompt


class AgentNodes:
    """Collection of LangGraph node functions with injected dependencies."""

    def __init__(self) -> None:
        """Initialize AgentNodes."""
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        self.retriever = Retriever()
        self.generator = Generator()

    def retrieve(self, state: dict[str, Any]) -> dict[str, Any]:
        """Retrieve context chunks based on the query."""
        if state.get("context_chunks"):
            return state

        limit = state.get("limit", DEFAULT_CHUNKS_RETRIEVAL_LIMIT)
        threshold = state.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
        query = state["query"]

        if "extracted_metadata" not in state:
            state["extracted_metadata"] = self.extract_query_metadata(query)

        metadata = state["extracted_metadata"]

        chunks = self.retriever.retrieve(
            query=query,
            limit=limit,
            similarity_threshold=threshold,
            content_types=metadata.get("entity_types"),
        )

        filtered_chunks = self.filter_chunks_by_metadata(chunks, metadata, limit)

        state["context_chunks"] = filtered_chunks[:limit]
        return state

    def generate(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate an answer using the retrieved context."""
        iteration = state.get("iteration", 0) + 1
        feedback = state.get("feedback")
        query = state["query"]
        augmented_query = (
            query if not feedback else f"{query}\\n\\nRevise per feedback:\\n{feedback}"
        )

        answer = self.generator.generate_answer(
            query=augmented_query,
            context_chunks=state.get("context_chunks", []),
        )

        history = state.get("history", [])
        history.append(
            {
                "iteration": iteration,
                "feedback": feedback,
                "query": augmented_query,
                "answer": answer,
            }
        )

        state.update(
            {"answer": answer, "iteration": iteration, "history": history, "feedback": None}
        )
        return state

    def evaluate(self, state: dict[str, Any]) -> dict[str, Any]:
        """Evaluate the generated answer and decide on the next step."""
        answer = state.get("answer", "")
        evaluation = self.call_evaluator(
            query=state["query"],
            answer=answer,
            context_chunks=state.get("context_chunks", []),
        )

        history = state.get("history", [])
        if history:
            history[-1]["evaluation"] = evaluation

        if "missing context" in evaluation.get("justification", "").lower():
            limit = state.get("limit", DEFAULT_CHUNKS_RETRIEVAL_LIMIT) * 2
            threshold = state.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD) * 0.95

            metadata = state.get("extracted_metadata", {})

            new_chunks = self.retriever.retrieve(
                query=state["query"],
                limit=limit,
                similarity_threshold=threshold,
                content_types=metadata.get("entity_types"),
            )

            filtered_chunks = self.filter_chunks_by_metadata(new_chunks, metadata, limit)
            state["context_chunks"] = filtered_chunks[:limit]

            state["feedback"] = "Expand and refine answer using newly retrieved context."
        else:
            state["feedback"] = evaluation.get("feedback") or None

        state.update({"evaluation": evaluation, "history": history})
        return state

    def route_from_evaluation(self, state: dict[str, Any]) -> str:
        """Route the workflow based on the evaluation result."""
        evaluation = state.get("evaluation") or {}
        iteration = state.get("iteration", 0)
        if evaluation.get("complete") or iteration >= DEFAULT_MAX_ITERATIONS:
            return "complete"
        return "refine"

    def filter_chunks_by_metadata(
        self,
        retrieved_chunks: list[dict[str, Any]],
        query_metadata: dict[str, Any],
        limit: int,
    ) -> list[dict[str, Any]]:
        """Rank and filter retrieved chunks using metadata and simple heuristics."""
        if not retrieved_chunks:
            return []

        requested_fields = query_metadata.get("requested_fields", [])
        query_filters = query_metadata.get("filters", {})

        if not requested_fields and not query_filters:
            return retrieved_chunks

        ranked_chunks: list[tuple[dict[str, Any], float]] = []
        for chunk in retrieved_chunks:
            relevance_score = 0.0
            chunk_metadata = chunk.get("additional_context", {})
            chunk_content = chunk.get("text", "").lower()

            for field_name in requested_fields:
                if chunk_metadata.get(field_name):
                    relevance_score += 2

            for filter_field, filter_value in query_filters.items():
                if filter_field in chunk_metadata:
                    metadata_value = chunk_metadata[filter_field]

                    if isinstance(metadata_value, str) and isinstance(filter_value, str):
                        if filter_value.lower() in metadata_value.lower():
                            relevance_score += 5

                    elif isinstance(metadata_value, list):
                        if any(
                            filter_value.lower() in str(item).lower() for item in metadata_value
                        ):
                            relevance_score += 5

                    elif metadata_value == filter_value:
                        relevance_score += 5

                if isinstance(filter_value, str) and filter_value.lower() in chunk_content:
                    relevance_score += 3

            if chunk_metadata:
                relevance_score += len(chunk_metadata) * 0.1

            ranked_chunks.append((chunk, relevance_score))

        ranked_chunks.sort(
            key=lambda entry: (entry[1], entry[0].get("similarity", 0)), reverse=True
        )

        return [chunk for chunk, _ in ranked_chunks[:limit]]

    def extract_query_metadata(self, query: str) -> dict[str, Any]:
        """Extract metadata from the user's query using an LLM."""
        metadata_extractor_prompt = Prompt.get_metadata_extractor_prompt()

        if not metadata_extractor_prompt:
            error_msg = "Prompt with key 'metadata-extractor-prompt' not found."
            raise ObjectDoesNotExist(error_msg)

        try:
            response = self.openai_client.chat.completions.create(
                model=DEFAULT_REASONING_MODEL,
                messages=[
                    {"role": "system", "content": metadata_extractor_prompt},
                    {"role": "user", "content": f"Query: {query}"},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            content = extract_json_from_markdown(content)
            return json.loads(content)

        except openai.OpenAIError:
            return {
                "requested_fields": [],
                "entity_types": [],
                "filters": {},
                "intent": "general query",
            }

    def call_evaluator(
        self, *, query: str, answer: str, context_chunks: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call the evaluator LLM to assess the quality of the generated answer."""
        formatted_context = self.generator.prepare_context(context_chunks)
        evaluation_prompt = (
            f"User Query:\\n{query}\\n\\n"
            f"Candidate Answer:\\n{answer}\\n\\n"
            f"Context Provided:\\n{formatted_context}\\n\\n"
            "Respond with the mandated JSON object."
        )

        evaluator_system_prompt = Prompt.get_evaluator_system_prompt()

        if not evaluator_system_prompt:
            error_msg = "Prompt with key 'evaluator-system-prompt' not found."
            raise ObjectDoesNotExist(error_msg)

        try:
            response = self.openai_client.chat.completions.create(
                model=DEFAULT_REASONING_MODEL,
                messages=[
                    {"role": "system", "content": evaluator_system_prompt},
                    {"role": "user", "content": evaluation_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            content = extract_json_from_markdown(content)
            return json.loads(content)

        except openai.OpenAIError:
            return {
                "complete": False,
                "feedback": "Evaluator error or invalid response.",
                "justification": "Evaluator error or invalid response.",
            }
