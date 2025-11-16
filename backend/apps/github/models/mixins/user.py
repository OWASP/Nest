"""GitHub user model mixins for index-related functionality."""

from django.db.models import Q

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin providing properties for indexing user data."""

    @property
    def is_indexable(self) -> bool:
        """
        Returns whether the user should be indexed.

        Purpose: Determines if the user is eligible for search indexing,
        considering if the user is a bot or belongs to non-indexable logins.
        """
        return (
            not self.is_bot
            and not self.login.endswith(("Bot", "-bot"))
            and self.login not in self.get_non_indexable_logins()
        )

    @property
    def idx_avatar_url(self) -> str:
        """
        Returns the user's avatar URL.

        Purpose: Provides image metadata for search indexing or display.
        """
        return self.avatar_url

    @property
    def idx_badge_count(self) -> int:
        """
        Returns the count of active badges the user has.

        Purpose: Measures user recognition or achievements for indexing.
        """
        return self.user_badges.filter(is_active=True).count()

    @property
    def idx_bio(self) -> str:
        """
        Returns the user's bio.

        Purpose: Provides textual metadata for indexing and searchability.
        """
        return self.bio

    @property
    def idx_company(self) -> str:
        """
        Returns the user's associated company.

        Purpose: Enables company-based filtering or indexing of users.
        """
        return self.company

    @property
    def idx_created_at(self) -> float:
        """
        Returns the user's account creation timestamp.

        Purpose: Useful for sorting and indexing users by creation date.
        """
        return self.created_at.timestamp()

    @property
    def idx_email(self) -> str:
        """
        Returns the user's email.

        Purpose: Provides contact information if indexing or display requires it.
        """
        return self.email

    @property
    def idx_key(self) -> str:
        """
        Returns the user's unique key (login).

        Purpose: Provides a unique identifier for indexing and linking users.
        """
        return self.login

    @property
    def idx_followers_count(self) -> int:
        """
        Returns the number of followers the user has.

        Purpose: Indicates user popularity and helps with ranking in search.
        """
        return self.followers_count

    @property
    def idx_following_count(self) -> int:
        """
        Returns the number of users the user is following.

        Purpose: Provides engagement metrics for indexing and analytics.
        """
        return self.following_count

    @property
    def idx_location(self) -> str:
        """
        Returns the user's location.

        Purpose: Enables geographic or location-based filtering and indexing.
        """
        return self.location

    @property
    def idx_login(self) -> str:
        """
        Returns the user's login name.

        Purpose: Provides an identifier for indexing and search.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """
        Returns the user's full name.

        Purpose: Useful for display and search indexing.
        """
        return self.name

    @property
    def idx_public_repositories_count(self) -> int:
        """
        Returns the number of public repositories owned by the user.

        Purpose: Measures user activity and contribution for indexing.
        """
        return self.public_repositories_count

    @property
    def idx_title(self) -> str:
        """
        Returns the user's professional title.

        Purpose: Provides metadata for display and search indexing.
        """
        return self.title

    @property
    def idx_contributions(self) -> list[dict]:
        """
        Returns a list of repository contributions for indexing.

        Purpose: Provides detailed contribution information including counts,
        repository metadata, license, owner, and latest release information.
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
        Returns the total contributions count of the user.

        Purpose: Provides a summary metric of user activity for indexing.
        """
        return self.contributions_count

    @property
    def idx_issues(self) -> list[dict]:
        """
        Returns a list of issues created by the user for indexing.

        Purpose: Provides detailed issue metadata for search indexing including
        creation time, repository info, comments count, and URL.
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
        Returns the total number of issues created by the user.

        Purpose: Provides a metric of user activity for indexing.
        """
        return self.issues.count()

    @property
    def idx_releases(self) -> list[dict]:
        """
        Returns a list of releases created by the user for indexing.

        Purpose: Provides detailed release metadata including pre-release status,
        repository info, publish date, tag name, and URL.
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
        Returns the total number of releases created by the user.

        Purpose: Provides a metric of user activity for indexing.
        """
        return self.releases.count()

    @property
    def idx_updated_at(self) -> float:
        """
        Returns the timestamp of the user's last profile update.

        Purpose: Useful for sorting and indexing users by recent activity.
        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """
        Returns the GitHub profile URL of the user.

        Purpose: Provides a reference URL for display or indexing.
        """
        return self.url
