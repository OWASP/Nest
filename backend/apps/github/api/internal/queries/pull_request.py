"""Github pull requests GraphQL queries."""

import strawberry
from django.db.models import OuterRef, Subquery

from apps.github.api.internal.nodes.pull_request import PullRequestNode
from apps.github.models.pull_request import PullRequest
from apps.owasp.models.project import Project


@strawberry.type
class PullRequestQuery:
    """Pull request queries."""

    @strawberry.field
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
        queryset = (
            PullRequest.objects.select_related(
                "author",
                "repository",
                "repository__organization",
            )
            .exclude(
                author__is_bot=True,
            )
            .order_by(
                "-created_at",
            )
        )

        if login:
            queryset = queryset.filter(author__login=login)

        if organization:
            queryset = queryset.filter(
                repository__organization__login=organization,
            )

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
            latest_pull_request_per_author = (
                queryset.filter(
                    author_id=OuterRef("author_id"),
                )
                .order_by(
                    "-created_at",
                )
                .values("id")[:1]
            )
            queryset = queryset.filter(
                id__in=Subquery(latest_pull_request_per_author),
            ).order_by(
                "-created_at",
            )

        return queryset[:limit] if limit > 0 else []
