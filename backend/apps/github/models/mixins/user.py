"""GitHub user model mixins for index-related functionality."""

from django.db.models import Q
from typing import Any

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin."""

    @property
    def is_indexable(self) -> bool:
        """
        Return: bool — True when the user account should be indexed.

        Purpose:
            Indicates whether this user is eligible for indexing (not a bot,
            username not ending with Bot/-bot, and not in the non-indexable list).
        """
        return (
            not self.is_bot
            and not self.login.endswith(("Bot", "-bot"))
            and self.login not in self.get_non_indexable_logins()
        )

    @property
    def idx_avatar_url(self) -> str:
        """
        Return: str — absolute avatar URL (e.g. "https://avatars.githubusercontent.com/u/123?v=4").

        Purpose:
            Supplies the avatar URL used by search results and UI previews.
        """
        return self.avatar_url

    @property
    def idx_badge_count(self) -> int:
        """
        Return: int — number of active badges (e.g. 3).

        Purpose:
            Exposes how many active badges the user has for indexing and profile summaries.
        """
        return self.user_badges.filter(is_active=True).count()

    @property
    def idx_bio(self) -> str:
        """
        Return: str — user's biography / summary text.

        Purpose:
            Provides bio text used in full-text indexing and search snippets.
        """
        return self.bio

    @property
    def idx_company(self) -> str:
        """
        Return: str — company/organization name as listed on the profile.

        Purpose:
            Supplies employer/organization data for filtering and display.
        """
        return self.company

    @property
    def idx_created_at(self) -> float:
        """
        Return: float — UNIX timestamp of user creation (seconds since epoch).

        Purpose:
            Used to sort or filter users by account age in the index.
        """
        return self.created_at.timestamp()

    @property
    def idx_email(self) -> str:
        """
        Return: str — public email address for the user (if present).

        Purpose:
            Exposes email for indexing when available (used for contact or search).
        """
        return self.email

    @property
    def idx_key(self) -> str:
        """
        Return: str — unique key for the user in the index (login/username).

        Purpose:
            Provides the primary identifier for user index records.
        """
        return self.login

    @property
    def idx_followers_count(self) -> int:
        """
        Return: int — number of followers (e.g. 120).

        Purpose:
            Supplies follower count used as an influence/engagement signal.
        """
        return self.followers_count

    @property
    def idx_following_count(self) -> int:
        """
        Return: int — number of users this user is following (e.g. 10).

        Purpose:
            Exposes following count for indexing and simple engagement metrics.
        """
        return self.following_count

    @property
    def idx_location(self) -> str:
        """
        Return: str — user provided location string.

        Purpose:
            Supplies location for geo/region-based filtering and display.
        """
        return self.location

    @property
    def idx_login(self) -> str:
        """
        Return: str — login/username (e.g. 'alice').

        Purpose:
            Provides the login used across the site for linking and identification.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """
        Return: str — display name (e.g. 'Alice Johnson').

        Purpose:
            Supplies human-friendly name for search results and UI rendering.
        """
        return self.name

    @property
    def idx_public_repositories_count(self) -> int:
        """
        Return: int — number of public repositories (e.g. 7).

        Purpose:
            Exposes public repository count for ranking and filtering.
        """
        return self.public_repositories_count

    @property
    def idx_title(self) -> str:
        """
        Return: str — user's title/role if provided (e.g. 'Security Researcher').

        Purpose:
            Used in indexing and displayed in profile summaries.
        """
        return self.title

    @property
    def idx_contributions(self) -> list[dict[str, Any]]:
        """
        Return: list[dict] — top repository contribution records (limited list).

        Purpose:
            Returns a list of contribution summaries (contributions_count, repository metadata)
            for indexing and to show the user's top repository contributions.
        """
        from apps.github.models.repository_contributor import RepositoryContributor

        return [
            {
                "contributions_count": rc.contributions_count,
                "repository_contributors_count": rc.repository.contributors_count,
                "repository_description": rc.repository.description,
                "repository_forks_count": rc.repository.forks_count,
                "repository_key": rc.repository.key.lower(),
                "repository_name": rc.repository.name,
                "repository_latest_release": str(rc.repository.latest_release.summary)
                if rc.repository.latest_release
                else "",
                "repository_license": rc.repository.license,
                "repository_owner_key": rc.repository.owner.login.lower(),
                "repository_stars_count": rc.repository.stars_count,
            }
            for rc in RepositoryContributor.objects.filter(
                user=self,
            )
            .exclude(
                Q(repository__is_fork=True)
                | Q(repository__organization__is_owasp_related_organization=False)
                | Q(user__login__in=self.get_non_indexable_logins())
            )
            .order_by("-contributions_count")
            .select_related("repository")[:TOP_REPOSITORY_CONTRIBUTORS_LIMIT]
        ]

    @property
    def idx_contributions_count(self) -> int:
        """
        Return: int — total contributions count (e.g. 256).

        Purpose:
            Exposes the aggregated contributions count for ranking and filtering.
        """
        return self.contributions_count

    @property
    def idx_issues(self) -> list[dict[str, Any]]:
        """
        Return: list[dict] — recent issue summaries (limited list).

        Purpose:
            Returns issue metadata (created_at timestamp, comments_count, number,
            repository keys, title and url) for indexing and display.
        """
        return [
            {
                "created_at": i.created_at.timestamp(),
                "comments_count": i.comments_count,
                "number": i.number,
                "repository": {
                    "key": i.repository.key,
                    "owner_key": i.repository.owner.login,
                },
                "title": i.title,
                "url": i.url,
            }
            for i in self.issues.select_related(
                "repository",
                "repository__owner",
            ).order_by("-created_at")[:ISSUES_LIMIT]
        ]

    @property
    def idx_issues_count(self) -> int:
        """
        Return: int — number of issues created by the user.

        Purpose:
            Supplies the user's issue count used for engagement metrics and indexing.
        """
        return self.issues.count()

    @property
    def idx_releases(self) -> list[dict[str, Any]]:
        """
        Return: list[dict] — recent release summaries (limited list).

        Purpose:
            Returns release metadata (is_pre_release, name, published_at timestamp,
            repository keys, tag_name and url) for indexing recent user releases.
        """
        return [
            {
                "is_pre_release": r.is_pre_release,
                "name": r.name,
                "published_at": r.published_at.timestamp(),
                "repository": {
                    "key": r.repository.key,
                    "owner_key": r.repository.owner.login,
                },
                "tag_name": r.tag_name,
                "url": r.url,
            }
            for r in self.releases.select_related(
                "repository",
                "repository__owner",
            ).order_by("-published_at")[:RELEASES_LIMIT]
        ]

    @property
    def idx_releases_count(self) -> int:
        """
        Return: int — number of releases authored by the user.

        Purpose:
            Exposes release count used for indexing and profile summaries.
        """
        return self.releases.count()

    @property
    def idx_updated_at(self) -> float:
        """
        Return: float — UNIX timestamp of last profile update (seconds since epoch).

        Purpose:
            Used to determine recency for incremental indexing and ranking.
        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """
        Return: str — GitHub profile URL (e.g. "https://github.com/username").

        Purpose:
            Supplies the canonical profile URL used in the index and UI links.
        """
        return self.url
