from algoliasearch.query_suggestions.client import QuerySuggestionsClientSync
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create query suggestions for Algolia indices"

    def handle(self, *args, **kwargs):
        client = QuerySuggestionsClientSync(
            settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_WRITE_API_KEY, "eu"
        )
        print("Algolia client initialized")

        entity_configs = {
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
        }

        # Iterate over entity
        for entity, config in entity_configs.items():
            response = client.create_config(
                configuration_with_index={
                    "indexName": f"{settings.ENVIRONMENT.lower()}_{entity}_suggestions",
                    "sourceIndices": [
                        {
                            "indexName": f"{settings.ENVIRONMENT.lower()}_{entity}",
                            **config,
                        }
                    ],
                    "exclude": ["test"],
                }
            )
            print(
                f"Query Suggestions for {settings.ENVIRONMENT.lower()}_{entity}: {response}")
