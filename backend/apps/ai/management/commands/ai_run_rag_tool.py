"""A command for invoking RAG tool."""

from django.core.management.base import BaseCommand

from apps.ai.agent.tools.rag.rag_tool import RagTool
from apps.ai.common.constants import (
    DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
    DEFAULT_SIMILARITY_THRESHOLD,
)


class Command(BaseCommand):
    help = "Test the RagTool functionality with a sample query"

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            type=str,
            default="What is OWASP Foundation?",
            help="Query to test the Rag tool",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
            help="Maximum number of results to retrieve",
        )
        parser.add_argument(
            "--threshold",
            type=float,
            default=DEFAULT_SIMILARITY_THRESHOLD,
            help="Similarity threshold (0.0 to 1.0)",
        )
        parser.add_argument(
            "--content-types",
            nargs="+",
            default=None,
            help="Content types to filter by (e.g., project chapter)",
        )
        parser.add_argument(
            "--embedding-model",
            type=str,
            default="text-embedding-3-small",
            help="OpenAI embedding model",
        )
        parser.add_argument(
            "--chat-model",
            type=str,
            default="gpt-4o",
            help="OpenAI chat model",
        )

    def handle(self, *args, **options):
        try:
            rag_tool = RagTool(
                chat_model=options["chat_model"],
                embedding_model=options["embedding_model"],
            )
        except ValueError:
            self.stderr.write(self.style.ERROR("Initialization error"))
            return

        self.stdout.write("\nProcessing query...")
        result = rag_tool.query(
            content_types=options["content_types"],
            limit=options["limit"],
            question=options["query"],
            similarity_threshold=options["threshold"],
        )
        self.stdout.write(f"\nAnswer: {result}")
