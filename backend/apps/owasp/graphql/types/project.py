import graphene

from apps.common.schema import BaseModelType
from apps.github.graphql.types.issue import IssueType
from apps.github.graphql.types.release import ReleaseType
from apps.github.models.issue import Issue
from apps.github.models.release import Release
from apps.owasp.models.project import Project


class ProjectType(BaseModelType):
    recent_issues = graphene.List(
        IssueType,
        limit=graphene.Int(default_value=10),
        state=graphene.String(default_value="open"),
    )
    recent_releases = graphene.List(ReleaseType, limit=graphene.Int(default_value=10))

    class Meta:
        model = Project
        fields = (
            "id",
            "name",
            "key",
            "level",
            "type",
            "description",
            "leaders_raw",
            "contributors_count",
            "custom_tags",
            "forks_count",
            "stars_count",
            "open_issues_count",
            "languages",
            "created_at",
            "updated_at",
        )

    def resolve_recent_issues(self, info, limit=10, state="open"):
        return Issue.objects.filter(repository__in=self.repositories.all(), state=state).order_by(
            "-created_at"
        )[:limit]

    def resolve_recent_releases(self, info, limit=10):
        return Release.objects.filter(
            repository__in=self.repositories.all(), is_draft=False, published_at__isnull=False
        ).order_by("-published_at")[:limit]
