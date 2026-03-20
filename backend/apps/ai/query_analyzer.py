"""Query analyzer for determining query complexity."""

import contextlib
import logging

from crewai import Agent, Crew, Task

from apps.ai.common.intent import Intent
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env

logger = logging.getLogger(__name__)

INTENT_SEPARATOR = "| intent:"


def create_query_analyzer_agent() -> Agent:
    """Create query analyzer agent.

    Returns:
        Agent: Query analyzer agent configured for complexity analysis.

    """
    return Agent(
        role="Query Analyzer",
        goal=(
            "Analyze user queries to determine complexity, identify required expert "
            "agents, and decompose complex queries into sub-queries when needed."
        ),
        backstory=env.get_template("query_analyzer/backstory.jinja")
        .render(intent_names=", ".join(Intent.values()))  # nosemgrep: direct-use-of-jinja2
        .strip(),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )


def analyze_query(query: str) -> dict:
    """Analyze query to determine complexity and required agents.

    Args:
        query (str): User's question.

    Returns:
        dict: Analysis with 'is_simple' and 'sub_queries'
        (list of dicts with 'query' and 'intent').

    """
    analyzer_agent = create_query_analyzer_agent()

    task_template = env.get_template("query_analyzer/tasks/analyze.jinja")
    task_description = task_template.render(  # nosemgrep: direct-use-of-jinja2
        query=query, intents=Intent.descriptions()
    ).strip()

    analysis_task = Task(
        description=task_description,
        agent=analyzer_agent,
        expected_output="Query analysis with complexity assessment and required agents",
    )

    crew = Crew(
        agents=[analyzer_agent],
        tasks=[analysis_task],
        verbose=True,
        max_iter=5,
        max_rpm=10,
    )
    result = crew.kickoff()

    result_str = str(result)
    is_simple = True
    sub_queries = []

    for line in result_str.split("\n"):
        line_lower = line.lower().strip()
        if line_lower.startswith("issimple:"):
            with contextlib.suppress(ValueError):
                value = line.split(":", 1)[1].strip().lower()
                is_simple = value in ("true", "yes", "1")
        elif line_lower.startswith("subquery:"):
            content = line.split(":", 1)[1].strip()
            if INTENT_SEPARATOR in content.lower():
                separator_idx = content.lower().index(INTENT_SEPARATOR)
                query_part = content[:separator_idx].strip()
                intent_part = content[separator_idx + len(INTENT_SEPARATOR) :].strip().lower()
                if query_part and intent_part in Intent.values():
                    sub_queries.append({"query": query_part, "intent": intent_part})

    if not is_simple and not sub_queries:
        logger.warning("Query analysis returned no valid sub-queries for: %s", query)
        sub_queries = [{"query": query, "intent": Intent.RAG.value}]

    return {
        "is_simple": is_simple,
        "sub_queries": sub_queries,
    }
