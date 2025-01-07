"""A command to donload OWASP Nest index synonyms."""

from django.core.management.base import BaseCommand
from algoliasearch.query_suggestions.client import QuerySuggestionsClientSync
from django.conf import settings


class Command(BaseCommand):
    help = 'Create query suggestions for Algolia indices'

    def handle(self, *args, **kwargs):
        client = QuerySuggestionsClientSync(
            settings.ALGOLIA_APPLICATION_ID,
            settings.ALGOLIA_WRITE_API_KEY, "eu"
        )
        print("Algolia client initialized")
        response_issues = client.create_config(
            configuration_with_index={
                "indexName": f"{settings.ENVIRONMENT.lower()}_issues_suggestions",
                "sourceIndices": [
                    {
                        "indexName": f"{settings.ENVIRONMENT.lower()}_issues",
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
                ],
                "exclude": ["test"],
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f"Query Suggestions for {settings.ENVIRONMENT.lower()}_issues: {response_issues}"))

        response_chapters = client.create_config(
            configuration_with_index={
                "indexName": f"{settings.ENVIRONMENT.lower()}_chapters_suggestions",
                "sourceIndices": [
                    {
                        "indexName": f"{settings.ENVIRONMENT.lower()}_chapters",
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
                ],
                "exclude": ["test"],
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f"Query Suggestions for {settings.ENVIRONMENT.lower()}_chapters: {response_chapters}"))

        response_projects = client.create_config(
            configuration_with_index={
                "indexName": f"{settings.ENVIRONMENT.lower()}_projects_suggestions",
                "sourceIndices": [
                    {
                        "indexName": f"{settings.ENVIRONMENT.lower()}_projects",
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
                ],
                "exclude": ["test"],
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f"Query Suggestions for {settings.ENVIRONMENT.lower()}_projects: {response_projects}"))

        response_committees = client.create_config(
            configuration_with_index={
                "indexName": f"{settings.ENVIRONMENT.lower()}_committees_suggestions",
                "sourceIndices": [
                    {
                        "indexName": f"{settings.ENVIRONMENT.lower()}_committees",
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
                ],
                "exclude": ["test"],
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f"Query Suggestions for {settings.ENVIRONMENT.lower()}_committees: {response_committees}"))
