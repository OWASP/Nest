"""Community Expert Agent for OWASP community member queries."""

from crewai import Agent

from apps.ai.agents.community.tools import (
    get_entity_channels,
    get_entity_leaders,
)
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_community_agent(allow_delegation: bool = False) -> Agent:
    """Create Community Expert Agent.

    Args:
        allow_delegation (bool): Whether the agent can delegate tasks. Defaults to False.

    Returns:
        Agent: Community Expert Agent configured with community tools

    """
    return Agent(
        role="OWASP Community Specialist",
        goal=(
            "Help users find information about OWASP community members, leaders, and entity "
            "channels. Use get_entity_leaders() to find who leads specific projects, chapters, "
            "or committees, or what entities a person leads. Use get_entity_channels() to find "
            "Slack channels related to specific OWASP entities. Always use tools to retrieve "
            "current information - do not rely on training data."
        ),
        backstory=env.get_template("agents/community/backstory.jinja").render().strip(),
        tools=[
            get_entity_channels,
            get_entity_leaders,
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=allow_delegation,
        memory=False,
    )
