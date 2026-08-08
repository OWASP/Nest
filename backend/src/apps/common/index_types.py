"""Type definitions for search index results."""

from __future__ import annotations

from typing import TypedDict


class UserSearchHit(TypedDict, total=False):
    """GitHub user search hit."""

    idx_bio: str | None
    idx_company: str | None
    idx_followers_count: int
    idx_following_count: int
    idx_location: str | None
    idx_login: str
    idx_name: str | None
    idx_public_repositories_count: int
    idx_url: str


class ChapterSearchHit(TypedDict, total=False):
    """OWASP chapter search hit."""

    idx_country: str
    idx_key: str
    idx_leaders: list[str]
    idx_name: str
    idx_suggested_location: str | None
    idx_summary: str
    idx_url: str


class CommitteeSearchHit(TypedDict, total=False):
    """OWASP committee search hit."""

    idx_leaders: list[str]
    idx_name: str
    idx_summary: str
    idx_url: str


class IssueSearchHit(TypedDict, total=False):
    """GitHub issue search hit."""

    idx_project_name: str
    idx_project_url: str
    idx_summary: str
    idx_title: str
    idx_url: str


class ProjectSearchHit(TypedDict, total=False):
    """OWASP project search hit."""

    idx_contributors_count: int
    idx_forks_count: int
    idx_key: str
    idx_leaders: list[str]
    idx_name: str
    idx_stars_count: int
    idx_summary: str
    idx_updated_at: int
    idx_url: str


class UserSearchResult(TypedDict):
    """Result returned by a GitHub user search."""

    hits: list[UserSearchHit]
    nbPages: int


class ChapterSearchResult(TypedDict):
    """Result returned by an OWASP chapter search."""

    hits: list[ChapterSearchHit]
    nbPages: int


class CommitteeSearchResult(TypedDict):
    """Result returned by an OWASP committee search."""

    hits: list[CommitteeSearchHit]
    nbPages: int


class IssueSearchResult(TypedDict):
    """Result returned by a GitHub issue search."""

    hits: list[IssueSearchHit]
    nbPages: int


class ProjectSearchResult(TypedDict):
    """Result returned by an OWASP project search."""

    hits: list[ProjectSearchHit]
    nbPages: int
