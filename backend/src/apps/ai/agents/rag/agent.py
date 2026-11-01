"""RAG Agent for complex OWASP questions requiring context retrieval."""

from crewai import Agent

from apps.ai.agents.rag.tools import semantic_search
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_rag_agent() -> Agent:
    """Create RAG Agent.

    Returns:
        Agent: RAG Agent configured with semantic search tools

    """
    return Agent(
        role="OWASP Knowledge Specialist",
        goal=(
            "Answer complex OWASP questions using retrieved context from OWASP documentation "
            "ONLY. Never rely on general knowledge or training data. Always use semantic search "
            "to find relevant content and synthesize information from retrieved sources only."
        ),
        backstory=env.get_template("agents/rag/backstory.jinja").render().strip(),
        tools=[semantic_search],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
