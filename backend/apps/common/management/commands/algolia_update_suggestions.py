"""A command to update OWASP Nest suggestions index."""

from algoliasearch.query_suggestions.client import QuerySuggestionsClientSync
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create query suggestions for Algolia indices"

    def handle(self, *args, **kwargs):
        client = QuerySuggestionsClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY,
            settings.ALGOLIA_APPLICATION_REGION,
        )

        entity_configs = {
            "chapters": {
                "facets": [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_tags"},
                    {"attribute": "idx_country"},
                    {"attribute": "idx_region"},
                    {"attribute": "idx_suggested_location"},
                ],
                "generate": [
                    ["idx_name"],
                    ["idx_tags"],
                    ["idx_country"],
                    ["idx_region"],
                    ["idx_suggested_location"],
                ],
            },
            "committees": {
                "facets": [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_tags"},
                ],
                "generate": [
                    ["idx_name"],
                    ["idx_tags"],
                ],
            },
            "issues": {
                "facets": [
                    {"attribute": "idx_title"},
                    {"attribute": "idx_project_name"},
                    {"attribute": "idx_repository_name"},
                    {"attribute": "idx_project_tags"},
                    {"attribute": "idx_repository_topics"},
                ],
                "generate": [
                    ["idx_title"],
                    ["idx_project_name"],
                    ["idx_repository_name"],
                    ["idx_project_tags"],
                    ["idx_repository_topics"],
                ],
            },
            "projects": {
                "facets": [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_repository_names"},
                    {"attribute": "idx_tags"},
                ],
                "generate": [
                    ["idx_name"],
                    ["idx_tags"],
                    ["idx_repository_names"],
                ],
            },
        }

        for entity, suggestion_settings in entity_configs.items():
            source_index_name = f"{settings.ENVIRONMENT.lower()}_{entity}"
            suggestions_index_name = f"{settings.ENVIRONMENT.lower()}_{entity}_suggestions"

            configuration = {
                "sourceIndices": [
                    {
                        "indexName": source_index_name,
                        **suggestion_settings,
                    }
                ]
            }
            client.update_config(
                index_name=suggestions_index_name,
                configuration=configuration,
            )
            print(f"Updated query suggestions index for {entity.capitalize()}")
