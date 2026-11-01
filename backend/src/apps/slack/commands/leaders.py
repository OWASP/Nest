"""Slack bot leaders command."""

from apps.common.utils import get_absolute_url
from apps.slack.commands.command import CommandBase


class Leaders(CommandBase):
    """Slack bot /leaders command."""

    def get_context(self, command: dict):
        """Get the template context.

        Args:
            command (dict): The Slack command payload.

        Returns:
            dict: The template context.

        """
        from apps.owasp.index.search.chapter import get_chapters
        from apps.owasp.index.search.project import get_projects

        search_query = command["text"].strip()

        attributes = ["idx_key", "idx_leaders", "idx_name"]
        searchable_attributes = ["idx_leaders", "idx_name"]
        limit = 5

        chapters = [
            {
                "idx_key": chapter["idx_key"],
                "idx_leaders": chapter["idx_leaders"],
                "idx_name": chapter["idx_name"],
                "url": get_absolute_url(f"/chapters/{chapter['idx_key']}"),
            }
            for chapter in get_chapters(
                query=search_query,
                attributes=attributes,
                limit=limit,
                page=1,
                searchable_attributes=searchable_attributes,
            )["hits"]
        ]
        projects = [
            {
                "idx_key": project["idx_key"],
                "idx_leaders": project["idx_leaders"],
                "idx_name": project["idx_name"],
                "url": get_absolute_url(f"/projects/{project['idx_key']}"),
            }
            for project in get_projects(
                query=search_query,
                attributes=attributes,
                limit=limit,
                page=1,
                searchable_attributes=searchable_attributes,
            )["hits"]
        ]
        return {
            **super().get_context(command),
            "CHAPTERS": chapters,
            "PROJECTS": projects,
            "SEARCH_QUERY": search_query,
        }
