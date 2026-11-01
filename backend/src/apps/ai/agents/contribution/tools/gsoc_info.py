"""Tool for getting general GSoC information."""

from crewai.tools import tool
from django.utils import timezone

from apps.ai.common.decorators import render_template
from apps.common.utils import get_absolute_url

MARCH = 3


@tool("Get general information about OWASP's Google Summer of Code program")
def get_gsoc_info() -> str:
    """Get general information about OWASP's participation in Google Summer of Code.

    Use this tool when users ask about:
    - What is GSoC with OWASP
    - How to get started with GSoC
    - OWASP GSoC program information
    - Google Summer of Code with OWASP
    - GSoC general information

    Returns:
        Formatted string with GSoC general information

    """
    return render_template(
        "agents/contribution/tools/get_gsoc_info.jinja",
        context_factory=lambda: {
            "gsoc_year": timezone.now().year
            if timezone.now().month >= MARCH
            else timezone.now().year - 1,
            "projects_url": get_absolute_url("/projects"),
        },
    )
