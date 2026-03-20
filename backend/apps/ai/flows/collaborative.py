"""Collaborative flow for multi-agent query processing."""

from __future__ import annotations

import logging

from apps.ai.agents.synthesizer import create_synthesizer_agent
from apps.ai.template_loader import env
from apps.ai.utils import get_fallback_response, get_intent_to_agent_map

logger = logging.getLogger(__name__)


def handle_collaborative_query(query: str, sub_queries: list[dict]) -> str:
    """Handle complex queries requiring multiple expert agents.

    Args:
        query: Original user query.
        sub_queries: List of dicts with 'query' and 'intent' keys from the query analyzer.

    Returns:
        Synthesized response string

    """
    from apps.ai.flows.assistant import execute_task  # noqa: PLC0415

    try:
        responses: list[tuple[str, str]] = []

        for sub_query in sub_queries:
            agent_factory = get_intent_to_agent_map().get(sub_query["intent"])
            if not agent_factory:
                logger.warning("Unknown agent in collaborative flow: %s", sub_query["intent"])
                continue

            agent = agent_factory()
            response = execute_task(agent, sub_query["query"])
            responses.append((sub_query["intent"], response))

        synthesizer_agent = create_synthesizer_agent()

        task_template = env.get_template("agents/synthesizer/tasks/synthesize.jinja")
        task_description = task_template.render(  # nosemgrep: direct-use-of-jinja2
            query=query, agent_responses=responses
        ).strip()
        return execute_task(synthesizer_agent, task_description=task_description)

    except Exception:
        logger.exception("Failed to process query: %s", query)
        return get_fallback_response()
