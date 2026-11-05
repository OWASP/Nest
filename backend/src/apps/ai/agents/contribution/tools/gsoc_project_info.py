"""Tool for getting GSoC project information."""

from crewai.tools import tool

from apps.owasp.utils.gsoc import get_gsoc_projects


@tool("Get OWASP GSoC projects for a specific year")
def get_gsoc_project_info(year: int) -> str:
    """Get OWASP projects that participated in Google Summer of Code for a specific year.

    Use this tool when users ask about:
    - GSoC projects for a specific year
    - What projects participated in GSoC [year]
    - OWASP GSoC [year] projects
    - List of GSoC projects by year

    Args:
        year: The GSoC year (e.g., 2024, 2025)

    Returns:
        Formatted string with GSoC projects for the specified year

    """
    projects = get_gsoc_projects(year)

    if not projects:
        return f"No GSoC projects found for year {year}."

    formatted = f"📦 *OWASP GSoC {year} Projects:*\n\n"

    for project in sorted(projects, key=lambda p: p.get("name", "")):
        name = project.get("name", "Unknown")
        url = project.get("url", "")

        formatted += f"• <{url}|*{name}*>\n"

    formatted += (
        f"\n💡 *Tip*: Use these project tags (e.g., `gsoc{year}`) "
        "to find more information on OWASP Nest."
    )

    return formatted
