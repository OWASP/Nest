"""Github pull requests GraphQL queries."""

import strawberry
import strawberry_django
from django.db.models import F, Window
from django.db.models.functions import Rank

from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.models.pull_request import PullRequest
from apps.owasp.models.project import Project

MAX_LIMIT = 1000


@strawberry.type
class PullRequestQuery:
    """Pull request queries."""

    @strawberry_django.field(
        select_related=[
            "author__owasp_profile",
            "author__user_badges__badge",
            "milestone__author__owasp_profile",
            "milestone__author__user_badges__badge",
            "repository__organization",
            "milestone__repository__organization",
        ],
        prefetch_related=[
            "assignees__owasp_profile",
            "assignees__user_badges__badge",
            "labels",
            "related_issues__repository__organization",
            "related_issues__assignees__user_badges__badge",
            "related_issues__labels",
            "related_issues__milestone__author",
            "related_issues__level",
        ],
    )
    def recent_pull_requests(
        self,
        *,
        distinct: bool = False,
        limit: int = 5,
        login: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        repository: str | None = None,
    ) -> list[PullRequestNode]:
        """Resolve recent pull requests.

        Args:
            distinct (bool): Whether to return unique pull requests per author and repository.
            limit (int): Maximum number of pull requests to return.
            login (str, optional): Filter pull requests by a specific author's login.
            organization (str, optional): Filter pull requests by a specific organization's login.
            project (str, optional):  Filter pull requests by a specific project.
            repository (str, optional): Filter pull requests by a specific repository's login.

        Returns:
            list[PullRequestNode]: List of pull request nodes containing the
            filtered list of pull requests.

        """
        queryset = PullRequest.objects.exclude(
            author__is_bot=True,
        ).order_by(
            "-created_at",
        )

        filters = {}
        if login:
            filters["author__login"] = login

        if organization:
            filters["repository__organization__login"] = organization

        queryset = queryset.filter(**filters)

        if project:
            project_instance = Project.objects.filter(key__iexact=f"www-project-{project}").first()
            if project_instance:
                queryset = queryset.filter(
                    repository_id__in=project_instance.repositories.values_list("id", flat=True)
                )
            else:
                queryset = queryset.none()

        if repository:
            queryset = queryset.filter(repository__key__iexact=repository)

        if distinct:
            queryset = (
                queryset.annotate(
                    rank=Window(
                        expression=Rank(),
                        partition_by=[F("author_id")],
                        order_by=F("created_at").desc(),
                    )
                )
                .filter(rank=1)
                .order_by("-created_at")
            )

        return queryset[:limit] if (limit := min(limit, MAX_LIMIT)) > 0 else []
