"""Management command to benchmark and test the NestBot AI Assistant."""

from django.core.management.base import BaseCommand
from apps.ai.flows.assistant import process_query

class Command(BaseCommand):
    help = "Benchmark the NestBot AI Assistant with a set of test queries."

    def add_arguments(self, parser):
        parser.add_argument(
            "--query",
            type=str,
            help="Single query to test",
        )

    def handle(self, *args, **options):
        single_query = options.get("query")
        
        test_queries = [
            # Project Queries
            "What are the OWASP flagship projects?",
            "Tell me about the OWASP ZAP project.",
            
            # Chapter Queries
            "Is there an OWASP chapter in London?",
            "Find chapters in India.",
            
            # Contribution Queries
            "How can I contribute to OWASP?",
            "Are there any projects for GSoC?",
            
            # Community/Collaborative Queries
            "Who leads the OWASP SAMM project and how can I find its Slack channel?",
            "Find flagship projects and their leaders.",
            
            # RAG/Complex Queries
            "What is the OWASP Code of Conduct?",
            "Explain the OWASP project lifecycle."
        ]

        if single_query:
            test_queries = [single_query]

        self.stdout.write(self.style.SUCCESS(f"Starting benchmark for {len(test_queries)} queries...\n"))

        for query in test_queries:
            self.stdout.write(self.style.NOTICE(f"QUERY: {query}"))
            try:
                # Use a dummy channel ID to simulate specific flow logic
                response = process_query(query, channel_id="C_TEST_BENCHMARK", is_app_mention=True)
                self.stdout.write(self.style.HTTP_INFO(f"RESPONSE: {response or 'No response yielded.'}"))
            except Exception as e:
                 self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))
            self.stdout.write("-" * 50)
