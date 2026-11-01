"""Tool for suggesting the #contribute channel."""

from crewai.tools import tool

from apps.ai.common.decorators import render_template
from apps.slack.constants import OWASP_CONTRIBUTE_CHANNEL_ID


@tool("Suggest #contribute channel for contribution questions")
def suggest_contribute_channel() -> str:
    """Suggest the #contribute Slack channel for contribution-related questions.

    ALWAYS use this tool when the query contains ANY of these indicators:
    - Keywords: "contribute", "contributing", "contributor", "contributors", "get involved",
      "getting involved"
    - Questions about: "beginner-friendly issues", "starter issues", "new contributors",
      "good projects for"
    - Requests for: "contribution guidelines", "contribution opportunities", "contribution docs"
    - Expressions of interest: "interested in contributing", "excited to join",
      "looking forward to contributing"
    - Questions about: "how to start", "getting started", "how to get involved",
      "how contributors get involved"
    - Questions about: "how teams collaborate", "how projects are structured",
      "how to find issues"
    - Any mention of wanting to contribute, get involved, or find contribution opportunities

    This tool should be used AUTOMATICALLY when contribution intent is detected -
    do not ask which channel to use.

    Returns:
        Formatted string with channel suggestion message for #contribute channel

    """
    channel_id = OWASP_CONTRIBUTE_CHANNEL_ID.lstrip("#")
    return render_template(
        "agents/channel/tools/contribute.jinja",
        contribute_channel_id=channel_id,
    )
