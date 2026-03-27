from apps.ai.common.intent import Intent
from apps.ai.query_analyzer import parse_query_analyzer_agent_result


class TestParseQueryAnalyzerAgentResult:
    def test_default_is_simple_true_when_missing(self):
        result = "SUB_QUERY: Query only | INTENT: rag\n"

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is True
        assert sub_queries == [{"query": "Query only", "intent": Intent.RAG.value}]

    def test_discard_unknown_intent(self):
        result = "IS_SIMPLE: false\nSUB_QUERY: Something unknown | INTENT: unknown_intent\n"

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is False
        assert sub_queries == []

    def test_missing_and_malformed_separators_with_noise(self):
        result = (
            "IS_SIMPLE: false\n"
            "SUB_QUERY: Needs an intent but none provided\n"
            "SUB_QUERY: Bad separator |INTT: rag\n"
            "Random irrelevant line: do not parse\n"
            "SUB_QUERY: Finally valid | INTENT: rag\n"
        )

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is False
        assert sub_queries == [{"query": "Finally valid", "intent": Intent.RAG.value}]

    def test_parse_false_and_single_subquery(self):
        result = "IS_SIMPLE: false\nSUB_QUERY: GSoC info please | Intent: gsoc\n"

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is False
        assert sub_queries == [{"query": "GSoC info please", "intent": Intent.GSOC.value}]

    def test_parse_simple_and_subqueries_uppercase_labels(self):
        result = (
            "IS_SIMPLE: true\n"
            "SUB_QUERY: Find OWASP chapters | INTENT: chapter\n"
            "SUB_QUERY: Show projects | INTENT: project\n"
        )

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is True
        assert len(sub_queries) == 2
        assert sub_queries[0]["query"] == "Find OWASP chapters"
        assert sub_queries[0]["intent"] == Intent.CHAPTER.value
        assert sub_queries[1]["intent"] == Intent.PROJECT.value

    def test_whitespace_around_separator_and_intent_token(self):
        result = (
            "IS_SIMPLE:true\n"
            "SUB_QUERY:Query A| INTENT:rag\n"
            "SUB_QUERY:Query B | INTENT: rag\n"
            "SUB_QUERY:Query C | INTENT : rag\n"
            "SUB_QUERY:Query D | intent:rag\n"
        )

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is True
        intents = [s["intent"] for s in sub_queries]
        assert all(i == Intent.RAG.value for i in intents)
        assert len(sub_queries) == 4

    def test_whitespace_before_and_after_labels_and_values(self):
        result = "  IS_SIMPLE:   true  \n  SUB_QUERY:   Find me something   | INTENT:   rag   \n"

        is_simple, sub_queries = parse_query_analyzer_agent_result(result)

        assert is_simple is True
        assert sub_queries == [{"query": "Find me something", "intent": Intent.RAG.value}]
