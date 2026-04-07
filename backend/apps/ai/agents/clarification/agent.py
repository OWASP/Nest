"""Clarification Expert Agent for disambiguation and out-of-scope handling."""

from crewai import Agent

from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_clarification_agent() -> Agent:
    """Create Clarification Agent.

    Returns:
        Agent: Clarification Agent.

    """
    return Agent(
        role="Clarification Specialist",
        goal="Handle unclear or out-of-scope questions",
        backstory=env.get_template("agents/clarification/backstory.jinja").render().strip(),
        tools=[],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
