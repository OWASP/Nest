"""OWASP chapter-specific tools."""

from crewai.tools import tool

from apps.owasp.index.search.chapter import get_chapters

MAX_LEADERS_DISPLAY = 3


def format_chapter_results(hits: list) -> str:
    """Format chapter search results for display.

    Args:
        hits: List of chapter hits from Algolia search

    Returns:
        Formatted string with chapter information

    """
    if not hits:
        return "No chapters found."

    formatted = "🌍 *OWASP Chapters:*\n\n"

    for chapter in hits:
        name = chapter.get("idx_name", "Unknown")
        summary = chapter.get("idx_summary", "")
        url = chapter.get("idx_url", "")
        leaders = chapter.get("idx_leaders", [])

        formatted += f"• <{url}|*{name}*>"

        if leaders:
            leader_names = ", ".join(leaders[:MAX_LEADERS_DISPLAY])
            if len(leaders) > MAX_LEADERS_DISPLAY:
                leader_names += f" and {len(leaders) - MAX_LEADERS_DISPLAY} more"
            formatted += f"\n  👥 Leaders: {leader_names}"

        if summary:
            formatted += f"\n  {summary}"

        formatted += "\n\n"

    return formatted


@tool("Search for OWASP chapters by location or name")
def search_chapters(query: str, limit: int = 5) -> str:
    """Search for OWASP chapters by location, name, or other attributes.

    Use this tool when users ask about:
    - Finding chapters in a specific location
    - Searching for chapters by name
    - OWASP chapters in [city/country]
    - Local OWASP chapters

    Args:
        query: Search query (location, name, etc.)
        limit: Maximum number of results to return (default: 5)

    Returns:
        Formatted string with chapter search results

    """
    results = get_chapters(query, limit=limit)
    hits = results.get("hits", [])

    return format_chapter_results(hits)
