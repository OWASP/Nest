"""Fixed search results for RAG benchmarks.

Text contains paraphrased source snapshots.
Distances are artificial test values.

Sources:
    https://owasp.org/policy/owasp-word-mark-usage-guidelines
    https://devguide.owasp.org/code_of_conduct/
    https://owasp.org/policy/bylaws
    https://owasp.org/policy/code-of-conduct
"""

from copy import deepcopy

TRADEMARK_DOCUMENTS = [
    {
        "text": (
            "OWASP trademark policy requires licensed users to use logo "
            "artwork supplied by the Foundation. They must preserve the "
            "logo's proportions, colors, and arrangement. Use of the mark "
            "must not imply OWASP endorsement of a company or its products."
        ),
        "context": "OWASP Word Mark Usage Guidelines; snapshot checked 2026-11-15",
        "distance": 0.1,
    }
]

RAG_FIXTURES = {
    "rag-001": {
        "relevant": [
            {
                "text": (
                    "OWASP Foundation's bylaws describe its purpose as improving "
                    "software security. Its activities include supporting projects, "
                    "community events and chapters, educational resources, and "
                    "branding programs."
                ),
                "context": "OWASP Bylaws, Section 1.4; snapshot checked 2026-11-15",
                "distance": 0.1,
            }
        ],
        "irrelevant": deepcopy(TRADEMARK_DOCUMENTS),
        "empty": [],
    },
    "rag-002": {
        "relevant": deepcopy(TRADEMARK_DOCUMENTS),
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
    },
    "rag-003": {
        "relevant": [
            {
                "text": (
                    "OWASP's code of conduct policy requires participants in "
                    "OWASP activities to follow its rules. This includes speakers "
                    "participating in events. Participants must treat others "
                    "respectfully and must avoid harassment, intimidation, "
                    "discrimination and abusive conduct."
                ),
                "context": ("OWASP Code of Conduct; snapshot checked 2026-11-15"),
                "distance": 0.1,
            }
        ],
        "irrelevant": deepcopy(TRADEMARK_DOCUMENTS),
        "empty": [],
    },
}

for scenarios in RAG_FIXTURES.values():
    scenarios["mixed"] = deepcopy(scenarios["irrelevant"] + scenarios["relevant"])


def get_rag_fixture(case_id: str, scenario: str = "relevant") -> list[dict]:
    """Return independent search results for a configured case and scenario."""
    return deepcopy(RAG_FIXTURES[case_id][scenario])
