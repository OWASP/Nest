"""Tool for getting OWASP contribution information."""

from crewai.tools import tool

from apps.ai.common.decorators import render_template


@tool("Get OWASP contribution information and guide users to #contribute channel")
def get_contribute_info() -> str:
    """Get information about contributing to OWASP.

    This tool provides guidance on how to contribute to OWASP projects
    and suggests joining the #contribute Slack channel for more help.

    Use this tool when users ask about:
    - How to contribute to OWASP
    - Contributing to OWASP projects
    - Getting started with contributions
    - Ways to help OWASP

    Returns:
        Formatted string with contribution information and #contribute channel suggestion

    """
    return render_template("agents/contribution/tools/get_contribute_info.jinja")
