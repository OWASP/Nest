"""OWASP app sponsor index."""

from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register

from apps.common.index import IS_LOCAL_BUILD, LOCAL_INDEX_LIMIT
from apps.owasp.models.sponsor import Sponsor


@register(Sponsor)
class SponsorIndex(AlgoliaIndex):
    """Sponsor index."""

    index_name = "sponsors"
    fields = (
        "idx_name",
        "idx_sort_name",
        "idx_description",
        "idx_url",
        "idx_job_url",
        "idx_image_path",
        "idx_member_type",
        "idx_sponsor_type",
        "idx_is_member",
    )
    settings = {
        "attributesForFaceting": [
            "filterOnly(idx_name)",
            "filterOnly(idx_sort_name)",
            "idx_member_type",
            "idx_sponsor_type",
            "idx_is_member",
        ],
        "indexLanguages": ["en"],
        "customRanking": [
            "asc(idx_sort_name)",
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
            "unordered(idx_name)",
            "unordered(idx_sort_name)",
            "unordered(idx_member_type)",
            "unordered(idx_sponsor_type)",
        ],
    }
    should_index = "is_indexable"

    def get_queryset(self):
        """Get queryset."""
        qs = Sponsor.objects.all()
        return qs[:LOCAL_INDEX_LIMIT] if IS_LOCAL_BUILD else qs
