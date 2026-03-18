"""Query analyzer for determining query complexity."""

import contextlib
import logging

from crewai import Agent, Crew, Task

from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env

logger = logging.getLogger(__name__)

AGENT_DESCRIPTIONS = {
    "channel": "Routes users to appropriate Slack channels for their questions",
    "chapter": "Finds OWASP chapters, chapter leaders, and chapter activities worldwide",
    "community": "Finds community leaders, committees, and entity Slack channels",
    "contribution": "Helps find contribution opportunities and GSoC program information",
    "project": "Finds OWASP projects by topic, maturity level, or specific needs",
    "rag": "Searches OWASP documentation, policies, and repositories for general information",
}


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
        .render(agent_names=", ".join(AGENT_DESCRIPTIONS))  # nosemgrep: direct-use-of-jinja2
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
        dict: Analysis with 'is_simple', 'sub_queries', and 'required_agents'.

    """
    analyzer_agent = create_query_analyzer_agent()

    task_template = env.get_template("query_analyzer/tasks/analyze.jinja")
    agents = [{"name": name, "description": desc} for name, desc in AGENT_DESCRIPTIONS.items()]
    task_description = task_template.render(  # nosemgrep: direct-use-of-jinja2
        query=query, agents=agents
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
    sub_queries = [query]
    required_agents = []

    for line in result_str.split("\n"):
        line_lower = line.lower().strip()
        if line_lower.startswith("issimple:"):
            with contextlib.suppress(ValueError):
                value = line.split(":", 1)[1].strip().lower()
                is_simple = value in ("true", "yes", "1")
        elif line_lower.startswith("subqueries:"):
            value = line.split(":", 1)[1].strip()
            if value and value.lower() != "none":
                sub_queries = [q.strip() for q in value.split("|") if q.strip()]
        elif line_lower.startswith("requiredagents:"):
            value = line.split(":", 1)[1].strip().lower()
            if value and value != "none":
                required_agents = [
                    a.strip() for a in value.split(",") if a.strip() in AGENT_DESCRIPTIONS
                ]

    if not required_agents:
        logger.warning("Query analysis returned no valid agents for: %s", query)

    return {
        "is_simple": is_simple,
        "sub_queries": sub_queries,
        "required_agents": required_agents,
    }
