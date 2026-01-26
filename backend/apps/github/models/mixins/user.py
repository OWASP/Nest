"""GitHub user model mixins for index-related functionality."""

from django.db.models import Q

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin."""

    @property
    def is_indexable(self):
        """Determine if the user should be indexed.

        Returns:
            bool: True if the user meets all indexing criteria, False otherwise.

        """
        return (
            not self.is_bot
            and not self.login.endswith(("Bot", "-bot"))
            and self.login not in self.get_non_indexable_logins()
        )

    @property
    def idx_avatar_url(self) -> str:
        """Get the user's avatar URL for indexing.

        Returns:
            str: The URL of the user's avatar image.

        """
        return self.avatar_url

    @property
    def idx_badge_count(self) -> int:
        """Get the number of active badges associated with the user.

        Returns:
            int: The count of active user badges.

        """
        return self.user_badges.filter(is_active=True).count()

    @property
    def idx_bio(self) -> str:
        """Get the user's biography text for indexing.

        Returns:
            str: The user's bio, if provided; otherwise an empty string.

        """
        return self.bio

    @property
    def idx_company(self) -> str:
        """Get the user's company affiliation for indexing.

        Returns:
            str: The company name associated with the user's profile, if any.

        """
        return self.company

    @property
    def idx_created_at(self) -> float:
        """Get the account creation timestamp for indexing.

        Returns:
            float: Unix timestamp when the account was created.

        """
        return self.created_at.timestamp()

    @property
    def idx_email(self) -> str:
        """Get the user's email address for indexing.

        Returns:
            str: The user's email address, if available.

        """
        return self.email

    @property
    def idx_key(self) -> str:
        """Get the unique key identifier for this user used in indexing.

        Returns:
            str: The user's login, used as the unique key.

        """
        return self.login

    @property
    def idx_followers_count(self) -> int:
        """Get the number of followers for the user.

        Returns:
            int: Total count of users following this user.

        """
        return self.followers_count

    @property
    def idx_following_count(self) -> int:
        """Get the number of users the user is following.

        Returns:
            int: Total count of users this user follows.

        """
        return self.following_count

    @property
    def idx_location(self) -> str:
        """Get the user's location for indexing.

        Returns:
            str: The user's self-declared location, if available.

        """
        return self.location

    @property
    def idx_login(self) -> str:
        """Get the user's login for indexing.

        Returns:
            str: The user's GitHub login handle.

        """
        return self.login

    @property
    def idx_name(self) -> str:
        """Get the user's display name for indexing.

        Returns:
            str: The full name displayed on the user's profile, if provided.

        """
        return self.name

    @property
    def idx_public_repositories_count(self) -> int:
        """Get the number of public repositories owned by the user.

        Returns:
            int: Total count of public repositories owned by the user.

        """
        return self.public_repositories_count

    @property
    def idx_title(self) -> str:
        """Get the user's profile title or headline for indexing.

        Returns:
            str: The title or headline associated with the user.

        """
        return self.title

    @property
    def idx_contributions(self):
        """Get a summary of the user's top repository contributions for indexing.

        Returns:
            list[dict]: A list of contribution summaries, each including counts and
                metadata about the contributed repositories (e.g., name, stars,
                forks, license, and latest release information).

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
        """Get the total number of contributions made by the user.

        Returns:
            int: Aggregate contributions count across repositories.

        """
        if hasattr(self, "owasp_profile") and self.owasp_profile.contributions_count:
            return self.owasp_profile.contributions_count
        return self.contributions_count

    @property
    def idx_issues(self) -> list[dict]:
        """Get recent issues associated with the user for indexing.

        Returns:
            list[dict]: A list of issue summaries including timestamps, counts,
                identifiers, titles, URLs, and minimal repository metadata.

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
        """Get the total number of issues associated with the user.

        Returns:
            int: Count of issues linked to the user.

        """
        return self.issues.count()

    @property
    def idx_releases(self) -> list[dict]:
        """Get releases associated with the user for indexing.

        Returns:
            list[dict]: A list of release summaries including pre-release flag,
                names, published timestamps, tags, URLs, and minimal repository
                metadata.

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
        """Get the total number of releases associated with the user.

        Returns:
            int: Count of releases linked to the user.

        """
        return self.releases.count()

    @property
    def idx_updated_at(self) -> float:
        """Get the last profile update timestamp for indexing.

        Returns:
            float: Unix timestamp (seconds since epoch) of the last update.

        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Get the user's GitHub profile URL for indexing.

        Returns:
            str: The URL to the user's GitHub profile page.

        """
        return self.url
