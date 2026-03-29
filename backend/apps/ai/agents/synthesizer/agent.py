"""Result Synthesizer Agent for combining multi-agent responses."""

from crewai import Agent

from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_synthesizer_agent() -> Agent:
    """Create Result Synthesizer Agent.

    Returns:
        Agent: Synthesizer Agent configured to combine multi-agent results.

    """
    return Agent(
        role="OWASP Result Synthesizer",
        goal=(
            "Combine results from multiple OWASP specialist agents into a single, "
            "coherent response. Remove duplicates, organize by relevance, and format "
            "for Slack markdown. Do NOT add information beyond what was provided."
        ),
        backstory=env.get_template("agents/synthesizer/backstory.jinja").render().strip(),
        tools=[],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
