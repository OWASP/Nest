"""Tool for suggesting the #gsoc channel."""

from crewai.tools import tool

from apps.ai.common.decorators import render_template
from apps.slack.constants import OWASP_GSOC_CHANNEL_ID


@tool("Suggest #gsoc channel for GSoC questions")
def suggest_gsoc_channel() -> str:
    """Suggest the #gsoc Slack channel for GSoC-related questions.

    Use this tool when:
    - Users ask questions about Google Summer of Code (GSoC) in the owasp-community channel
    - Users want to contribute to OWASP through GSoC and are in owasp-community channel
    - Users are interested in GSoC program information and asked in owasp-community channel

    Returns:
        Formatted string with channel suggestion message for #gsoc channel

    """
    channel_id = OWASP_GSOC_CHANNEL_ID.lstrip("#")
    return render_template(
        "agents/channel/tools/gsoc.jinja",
        gsoc_channel_id=channel_id,
    )
