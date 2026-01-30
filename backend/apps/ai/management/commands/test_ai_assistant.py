"""Management command to benchmark and test the NestBot AI Assistant."""

import traceback

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
            # Project-Related Queries (should route to Project Expert Agent)
            "What are the OWASP flagship projects?",
            "Tell me about the OWASP Top 10 project.",
            "Who leads the OWASP SAMM project?",
            "What is the OWASP ASVS project about?",
            "Find information about OWASP Juice Shop.",
            "Tell me about OWASP Dependency-Check.",
            "What are the OWASP project maturity levels?",
            "Find flagship projects and their leaders.",
            
            # Chapter-Related Queries (should route to Chapter Expert Agent)
            "Is there an OWASP chapter in London?",
            "Find OWASP chapters in India.",
            "Tell me about the OWASP Bay Area chapter.",
            "What chapters exist in the United States?",
            "Find OWASP chapters in Bangalore.",
            "Tell me about the OWASP Mumbai chapter.",
            
            # Committee-Related Queries
            "What does the OWASP Project Committee do?",
            "Tell me about OWASP committees.",
            
            # Event-Related Queries
            "What OWASP events are coming up?",
            "Tell me about OWASP AppSec events.",
            
            # Contribution & GSoC Queries (should route to Contribution Expert Agent)
            "How can I contribute to OWASP?",
            "Are there any OWASP projects for GSoC?",
            "How do I get started with application security?",
            
            # Multi-Intent / Collaborative Queries (should trigger multiple agents)
            "Who leads the OWASP SAMM project and how can I find its Slack channel?",
            "Find flagship projects and their leaders with their Slack channels.",
            
            # RAG / Complex Knowledge Queries (should route to RAG Agent)
            "What is the OWASP Code of Conduct?",
            "Explain the OWASP project lifecycle.",
            "What is OWASP?",
            "Tell me about web security.",
            
            # Edge Cases & Low Confidence Queries
            "Hello",
            "Thanks",
            "What is cybersecurity?",
        ]

        if single_query:
            test_queries = [single_query]

        self.stdout.write(self.style.SUCCESS(f"Starting benchmark for {len(test_queries)} queries...\n"))
        self.stdout.write(self.style.SUCCESS("=" * 70 + "\n"))

        results = {
            "total": len(test_queries),
            "success": 0,
            "failed": 0,
            "no_response": 0,
        }

        for idx, query in enumerate(test_queries, 1):
            self.stdout.write(self.style.NOTICE(f"\n[{idx}/{len(test_queries)}] QUERY: {query}"))
            self.stdout.write("-" * 70)
            try:
                # Use a dummy channel ID to simulate specific flow logic
                response = process_query(query, channel_id="C_TEST_BENCHMARK", is_app_mention=True)
                if response:
                    results["success"] += 1
                    # Truncate long responses for readability
                    response_preview = response[:500] + "..." if len(response) > 500 else response
                    self.stdout.write(self.style.HTTP_INFO(f"RESPONSE: {response_preview}"))
                else:
                    results["no_response"] += 1
                    self.stdout.write(self.style.WARNING("RESPONSE: No response yielded."))
            except Exception as e:
                results["failed"] += 1
                self.stdout.write(self.style.ERROR(f"ERROR: {str(e)}"))
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        # Print summary
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("\nSUMMARY:"))
        self.stdout.write(self.style.SUCCESS(f"  Total queries: {results['total']}"))
        self.stdout.write(self.style.HTTP_INFO(f"  Successful: {results['success']}"))
        self.stdout.write(self.style.WARNING(f"  No response: {results['no_response']}"))
        self.stdout.write(self.style.ERROR(f"  Failed: {results['failed']}"))
        self.stdout.write("=" * 70 + "\n")
