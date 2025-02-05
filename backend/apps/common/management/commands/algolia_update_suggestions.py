"""A command to update OWASP Nest suggestions index."""

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.common.index import IndexBase, should_create_index


class Command(BaseCommand):
    help = "Create query suggestions for Algolia indices"

    def handle(self, *args, **kwargs):
        client = IndexBase.get_suggestions_client()

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
                    {"attribute": "idx_repositories.name"},
                    {"attribute": "idx_tags"},
                ],
                "generate": [
                    ["idx_name"],
                    ["idx_tags"],
                    ["idx_repositories.name"],
                ],
            },
            "users": {
                "facets": [
                    {"attribute": "idx_key"},
                    {"attribute": "idx_name"},
                    {"attribute": "idx_title"},
                ],
                "generate": [
                    ["idx_name"],
                    ["idx_title"],
                ],
            },
        }

        print("\nThe following query suggestion index were updated:")
        for entity, suggestion_settings in entity_configs.items():
            source_index_name = f"{settings.ENVIRONMENT.lower()}_{entity}"
            suggestions_index_name = f"{settings.ENVIRONMENT.lower()}_{entity}_suggestions"

            # Skip updating if the index is excluded
            if not should_create_index(suggestions_index_name, "suggestion"):
                continue

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
            print(f"{7*' '} * {entity.capitalize()}")
