"""GitHub app index."""

from datetime import timedelta as td

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from django.db.models import Q
from django.utils import timezone

from apps.github.models.issue import Issue


@register(Issue)
class IssueIndex(AlgoliaIndex):
    """Issue index."""

    index_name = "issues"

    fields = (
        "idx_author_login",
        "idx_author_name",
        "idx_body",
        "idx_comments_count",
        "idx_created_at",
        "idx_labels",
        "idx_project_description",
        "idx_project_level",
        "idx_project_name",
        "idx_project_tags",
        "idx_repository_contributors_count",
        "idx_repository_description",
        "idx_repository_forks_count",
        "idx_repository_languages",
        "idx_repository_name",
        "idx_repository_stars_count",
        "idx_repository_topics",
        "idx_title",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
        "minProximity": 3,
        "indexLanguages": ["en"],
        "customRanking": [
            "desc(idx_created_at)",
            "desc(idx_updated_at)",
            "desc(idx_comments_count)",
            "desc(idx_repository_contributors_count)",
            "desc(idx_repository_stars_count)",
            "desc(idx_repository_forks_count)",
        ],
        "ranking": [
            "typo",
            "geo",
            "words",
            "filters",
            "proximity",
            "attribute",
            "exact",
            "custom",
        ],
        "searchableAttributes": [
            "unordered(idx_labels, idx_repository_languages)",
            "unordered(idx_title, idx_project_name, idx_repository_name)",
            "unordered(idx_project_description, idx_repository_description)",
            "unordered(idx_project_tags, idx_repository_topics)",
            "unordered(idx_author_login, idx_author_name)",
            "unordered(idx_body)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        # We index all unassigned issues and issues with no activity within 60 days.
        return (
            Issue.objects.select_related(
                "repository",
            )
            .prefetch_related(
                "assignees",
                "labels",
                "repository__project_set",
            )
            .filter(
                Q(assignees__isnull=True)
                | Q(assignees__isnull=False, updated_at__lte=timezone.now() - td(days=60))
            )
        )
