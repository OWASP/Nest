"""Management command for running the agentic RAG workflow."""

from django.core.management.base import BaseCommand

from apps.ai.agent.agent import AgenticRAGAgent


class Command(BaseCommand):
    """Execute the LangGraph agentic RAG workflow."""

    help = "Execute the LangGraph agentic RAG workflow"

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument(
            "--query",
            type=str,
            required=False,
            help="User query to answer",
            default="can you list all flagship projects?",
        )

    def handle(self, *args, **options):
        """Handle the command."""
        try:
            agent = AgenticRAGAgent()
        except ValueError as error:
            self.stderr.write(self.style.ERROR(str(error)))
            return

        result = agent.run(query=options["query"])

        self.stdout.write(self.style.SUCCESS("Agentic RAG workflow completed"))
        self.stdout.write(f"\nAnswer:\n{result.answer}")
