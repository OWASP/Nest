"""Slack bot leaders command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase


class Leaders(CommandBase):
    """Slack bot /leaders command."""

    def get_template_context(self, command):
        """Get the template context."""
        from apps.owasp.api.search.chapter import get_chapters
        from apps.owasp.api.search.project import get_projects

        search_query = command["text"].strip()

        attributes = ["idx_key", "idx_leaders", "idx_name"]
        searchable_attributes = ["idx_leaders", "idx_name"]
        limit = 5
        chapters = get_chapters(
            query=search_query,
            attributes=attributes,
            limit=limit,
            page=1,
            searchable_attributes=searchable_attributes,
        )["hits"]

        projects = get_projects(
            query=search_query,
            attributes=attributes,
            limit=limit,
            page=1,
            searchable_attributes=searchable_attributes,
        )["hits"]

        chapters_with_urls = [
            {
                "idx_key": chapter["idx_key"],
                "idx_name": chapter["idx_name"],
                "idx_leaders": chapter["idx_leaders"],
                "url": get_absolute_url(f"chapters/{chapter['idx_key']}"),
            }
            for chapter in chapters
        ]
        projects_with_urls = [
            {
                "idx_key": project["idx_key"],
                "idx_name": project["idx_name"],
                "idx_leaders": project["idx_leaders"],
                "url": get_absolute_url(f"projects/{project['idx_key']}"),
            }
            for project in projects
        ]
        return {
            **super().get_template_context(command),
            "chapters": chapters_with_urls,
            "projects": projects_with_urls,
            "search_query": search_query,
            "has_results": bool(chapters or projects),
        }
