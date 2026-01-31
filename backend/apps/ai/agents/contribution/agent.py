"""Contribution Expert Agent for OWASP contribution queries."""

from crewai import Agent

from apps.ai.agents.contribution.tools import (
    get_contribute_info,
    get_gsoc_info,
    get_gsoc_project_info,
)
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_contribution_agent(allow_delegation: bool = False) -> Agent:
    """Create Contribution Expert Agent.

    Args:
        allow_delegation (bool): Whether the agent can delegate tasks. Defaults to False.

    Returns:
        Agent: Contribution Expert Agent configured with contribution and GSoC tools

    """
    return Agent(
        role="OWASP Contribution Specialist",
        goal=(
            "Help users understand how to contribute to OWASP projects and participate in "
            "Google Summer of Code (GSoC) ONLY using the provided tools. Never rely on general "
            "knowledge or training data. Always use tools to retrieve current contribution and "
            "GSoC information."
        ),
        backstory=env.get_template("agents/contribution/backstory.jinja").render().strip(),
        tools=[
            get_contribute_info,
            get_gsoc_info,
            get_gsoc_project_info,
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=allow_delegation,
        memory=False,
    )
