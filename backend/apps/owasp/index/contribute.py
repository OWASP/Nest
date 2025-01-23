"""OWASP app chapter index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.common.index import IS_LOCAL_BUILD, LOCAL_INDEX_LIMIT
from apps.owasp.models.contribute import Contribute


@register(Contribute)
class ContributeIndex(AlgoliaIndex):
    """Contribute index."""

    index_name = "contributes"

    fields = (
        "idx_title",
        "idx_project",
        "idx_project_url",
        "idx_summary",
        "idx_url",
    )

    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_project)",
            "idx_title",
        ],
        "indexLanguages": ["en"],
        "customRanking": [
            "asc(idx_title)",
            "asc(idx_project)",
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
            "unordered(idx_title)",
            "unordered(idx_project)",
            "unordered(idx_summary)",
        ],
    }

    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        qs = Contribute.active_contributions.select_related(
            "related_project",
        )
        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs
