"""Project Expert Agent for OWASP project queries."""

from crewai import Agent

from apps.ai.agents.project.tools import (
    get_flagship_projects,
    get_incubator_projects,
    get_lab_projects,
    get_production_projects,
    get_project_age,
    search_projects,
)
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_project_agent(allow_delegation: bool = False) -> Agent:
    """Create Project Expert Agent.

    Args:
        allow_delegation (bool): Whether the agent can delegate tasks. Defaults to False.

    Returns:
        Agent: Project Expert Agent configured with project tools

    """
    return Agent(
        role="OWASP Project Specialist",
        goal=(
            "Provide accurate, detailed information about OWASP projects "
            "ONLY using the provided tools. Never rely on general knowledge or training data. "
            "Always use tools to retrieve current, accurate information about projects."
        ),
        backstory=env.get_template("agents/project/backstory.jinja").render().strip(),
        tools=[
            get_flagship_projects,
            get_production_projects,
            get_lab_projects,
            get_incubator_projects,
            get_project_age,
            search_projects,
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=allow_delegation,
        memory=False,
    )
