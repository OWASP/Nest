"""A command for invoking RAG tool."""

from django.core.management.base import BaseCommand

from apps.ai.agent.tools.RAG.rag_tool import RAGTool
from apps.ai.common.constants import DEFAULT_LIMIT, DEFAULT_SIMILARITY_THRESHOLD


class Command(BaseCommand):
    help = "Test the RAGTool functionality with a sample query"

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            type=str,
            default="What is OWASP Foundation?",
            help="Query to test the RAG tool",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=DEFAULT_LIMIT,
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
            rag_tool = RAGTool(
                embedding_model=options["embedding_model"],
                chat_model=options["chat_model"],
            )
        except ValueError:
            self.stderr.write(self.style.ERROR("Initialization error"))
            return

        query = options["query"]
        limit = options["limit"]
        threshold = options["threshold"]
        content_types = options["content_types"]

        self.stdout.write("\nProcessing query...")
        result = rag_tool.query(
            question=query,
            limit=limit,
            similarity_threshold=threshold,
            content_types=content_types,
        )
        self.stdout.write(f"\nAnswer: {result['answer']}")
