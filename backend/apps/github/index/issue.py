"""GitHub issue index."""

from algoliasearch_django import AlgoliaIndex

from apps.common.index import IS_LOCAL_BUILD, LOCAL_INDEX_LIMIT, IndexBase, conditional_register
from apps.github.models.issue import Issue


@conditional_register(Issue)
class IssueIndex(AlgoliaIndex, IndexBase):
    """Issue index."""

    index_name = "issues"

    fields = (
        "idx_author_login",
        "idx_author_name",
        "idx_comments_count",
        "idx_created_at",
        "idx_hint",
        "idx_labels",
        "idx_project_description",
        "idx_project_level",
        "idx_project_name",
        "idx_project_tags",
        "idx_project_url",
        "idx_repository_contributors_count",
        "idx_repository_description",
        "idx_repository_forks_count",
        "idx_repository_languages",
        "idx_repository_name",
        "idx_repository_stars_count",
        "idx_repository_topics",
        "idx_summary",
        "idx_title",
        "idx_updated_at",
        "idx_url",
    )

    settings = {
        "attributesForFaceting": [
            "idx_title",
            "idx_project_name",
            "idx_repository_name",
            "idx_project_tags",
            "idx_repository_topics",
        ],
        "attributeForDistinct": "idx_project_name",
        "minProximity": 4,
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
            "words",
            "filters",
            "proximity",
            "attribute",
            "exact",
            "custom",
        ],
        "searchableAttributes": [
            "unordered(idx_title, idx_project_name, idx_repository_name)",
            "unordered(idx_labels, idx_repository_languages)",
            "unordered(idx_project_description, idx_repository_description)",
            "unordered(idx_project_tags, idx_repository_topics)",
            "unordered(idx_author_login, idx_author_name)",
            "unordered(idx_summary)",
            "unordered(idx_project_level)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        qs = Issue.open_issues.assignable.select_related(
            "repository",
        ).prefetch_related(
            "assignees",
            "labels",
            "repository__project_set",
        )

        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs

    @staticmethod
    def update_synonyms():
        """Update synonyms."""
        return IssueIndex.reindex_synonyms("github", "issue")
