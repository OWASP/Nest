"""Chapter Expert Agent for OWASP chapter queries."""

from crewai import Agent

from apps.ai.agents.chapter.tools import search_chapters
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_chapter_agent(allow_delegation: bool = False) -> Agent:
    """Create Chapter Expert Agent.

    Returns:
        Agent: Chapter Expert Agent configured with chapter tools

    """
    return Agent(
        role="OWASP Chapter Specialist",
        goal=(
            "Help users find and connect with OWASP chapters "
            "ONLY using the provided tools. Never rely on general knowledge or training data. "
            "Always use tools to retrieve current chapter information."
        ),
        backstory=env.get_template("agents/chapter/backstory.jinja").render().strip(),
        tools=[search_chapters],
        llm=get_llm(),
        verbose=True,
        allow_delegation=allow_delegation,
        memory=False,
    )
