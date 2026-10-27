"""Fixed search results for the rag-002 trademark benchmark.

Text contains paraphrased source snapshots.
Distances are artificial test values.

Sources:
    https://policy.owasp.org/operational/mark-usage-guidelines.html
    https://devguide.owasp.org/code_of_conduct/
"""

from copy import deepcopy

RAG_FIXTURES = {
    "rag-002": {
        "relevant": [
            {
                "text": (
                    "OWASP trademark policy requires licensed users to use logo "
                    "artwork supplied by the Foundation. They must preserve the "
                    "logo's proportions, colors, and arrangement. Use of the mark "
                    "must not imply OWASP endorsement of a company or its products."
                ),
                "context": "repository www-policy: OWASP Word Mark Usage Guidelines",
                "distance": 0.1,
            }
        ],
        "irrelevant": [
            {
                "text": (
                    "The OWASP Developer Guide asks contributors to treat people "
                    "considerately, welcome different perspectives, and avoid "
                    "harassment or personal attacks."
                ),
                "context": "repository DevGuide: Contributor Code of Conduct",
                "distance": 0.1,
            }
        ],
        "empty": [],
    }
}


def get_rag_fixture(case_id: str, scenario: str = "relevant") -> list[dict]:
    """Return independent search results for a configured case and scenario."""
    return deepcopy(RAG_FIXTURES[case_id][scenario])
