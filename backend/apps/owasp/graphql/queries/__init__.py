"""OWASP GraphQL queries."""


from .chapter import ChapterQuery
from .committee import CommitteeQuery
from .project import ProjectQuery


class OwaspQuery(ChapterQuery, CommitteeQuery, EventQuery, ProjectQuery):
    """OWASP queries."""
