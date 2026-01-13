"""Channel Suggestion Agent for routing users to appropriate Slack channels."""

from crewai import Agent

from apps.ai.agents.channel.tools import (
    suggest_contribute_channel,
    suggest_gsoc_channel,
)
from apps.ai.common.llm_config import get_llm
from apps.ai.template_loader import env


def create_channel_agent() -> Agent:
    """Create Channel Suggestion Agent.

    Returns:
        Agent: Channel Suggestion Agent configured with channel suggestion tools

    """
    return Agent(
        role="OWASP Channel Router",
        goal=(
            "When questions are asked in the owasp-community channel, analyze the ENTIRE message "
            "(including greetings and introductions) to identify the user's intent, then "
            "automatically use the appropriate channel suggestion tool. For contribution-related "
            "queries, use suggest_contribute_channel(). For GSoC queries, "
            "use suggest_gsoc_channel(). "
            "DO NOT dismiss messages as 'general greetings' - always read the full content to "
            "find the actual questions and interests."
        ),
        backstory=env.get_template("agents/channel/backstory.jinja").render().strip(),
        tools=[
            suggest_contribute_channel,
            suggest_gsoc_channel,
        ],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
