"""OWASP project GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import Q

from apps.common.utils import normalize_limit
from apps.github.models.user import User as GithubUser
from apps.owasp.api.internal.nodes.project import ProjectNode
from apps.owasp.models.project import Project

MAX_RECENT_PROJECTS_LIMIT = 1000
MAX_SEARCH_QUERY_LENGTH = 100
MIN_SEARCH_QUERY_LENGTH = 3
SEARCH_PROJECTS_LIMIT = 3


@strawberry.type
class ProjectQuery:
    """Project queries."""

    @strawberry_django.field
    def project(self, key: str) -> ProjectNode | None:
        """Resolve project.

        Args:
            key (str): The key of the project.

        Returns:
            ProjectNode | None: The project node if found, otherwise None.

        """
        try:
            return Project.objects.get(key=f"www-project-{key}")
        except Project.DoesNotExist:
            return None

    @strawberry_django.field
    def recent_projects(self, limit: int = 8) -> list[ProjectNode]:
        """Resolve recent projects.

        Args:
            limit (int): The maximum number of recent projects to return.

        Returns:
            list[ProjectNode]: A list of recent active projects.

        """
        if (normalized_limit := normalize_limit(limit, MAX_RECENT_PROJECTS_LIMIT)) is None:
            return []

        return Project.objects.filter(is_active=True).order_by("-created_at")[:normalized_limit]

    @strawberry_django.field
    def search_projects(self, query: str) -> list[ProjectNode]:
        """Search active projects by name (case-insensitive, partial match)."""
        cleaned_query = query.strip()
        if (
            len(cleaned_query) < MIN_SEARCH_QUERY_LENGTH
            or len(cleaned_query) > MAX_SEARCH_QUERY_LENGTH
        ):
            return []

        return Project.objects.filter(
            is_active=True,
            name__icontains=cleaned_query,
        ).order_by("name")[:SEARCH_PROJECTS_LIMIT]

    @strawberry_django.field
    def is_project_leader(self, info: strawberry.Info, login: str) -> bool:
        """Check if a GitHub login or name is listed as a project leader."""
        try:
            github_user = GithubUser.objects.get(login=login)
        except GithubUser.DoesNotExist:
            return False

        user_tokens = {
            normalized_token
            for token in (github_user.login, github_user.name)
            if (normalized_token := self._normalize_leader_token(token))
        }
        if not user_tokens:
            return False

        leaders_raw_filter = Q()
        for token in user_tokens:
            leaders_raw_filter |= Q(leaders_raw__icontains=token)

        for leaders_raw in Project.objects.filter(leaders_raw_filter).values_list(
            "leaders_raw", flat=True
        ):
            leader_tokens = {
                normalized_token
                for leader in (leaders_raw or [])
                if (normalized_token := self._normalize_leader_token(leader))
            }
            if user_tokens & leader_tokens:
                return True

        return False

    @staticmethod
    def _normalize_leader_token(value: str | None) -> str:
        """Normalize a leader token for case-insensitive exact matching."""
        if not value:
            return ""

        return value.strip().lstrip("@").casefold()
