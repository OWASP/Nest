"""Formatting utilities for project tools."""


def format_project_results(hits: list, level_name: str = "") -> str:
    """Format project search results for display.

    Args:
        hits: List of project hits from Algolia search
        level_name: Optional level name to include in header

    Returns:
        Formatted string with project information

    """
    if not hits:
        return f"No projects found{f' at {level_name} level' if level_name else ''}."

    header = "📦 *OWASP Projects"
    if level_name:
        header += f" ({level_name})"
    header += ":*\n\n"

    formatted = header
    for project in hits:
        name = project.get("idx_name", "Unknown")
        summary = project.get("idx_summary", "")
        url = project.get("idx_url", "")
        stars = project.get("idx_stars_count", 0)
        contributors = project.get("idx_contributors_count", 0)
        level = project.get("idx_level", "").title()

        formatted += f"• <{url}|*{name}*>"
        if level:
            formatted += f" ({level})"
        formatted += "\n"

        if summary:
            formatted += f"  {summary}\n"

        stats = []
        if stars:
            stats.append(f"⭐ {stars}")
        if contributors:
            stats.append(f"👥 {contributors}")
        if stats:
            formatted += f"  {' | '.join(stats)}\n"

        formatted += "\n"

    return formatted
