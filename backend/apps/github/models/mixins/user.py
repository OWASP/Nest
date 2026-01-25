"""GitHub user model mixins for index-related functionality."""

from django.db.models import Q

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin."""

    @property
    def is_indexable(self):
        """Indicate whether the user should be indexed.

        A user is considered indexable if it is not a bot account,
        does not have a bot-like login, and is not part of the list
        of excluded logins.

        Returns:
            bool: True if the user should be indexed, False otherwise.
        """
        return (
            not self.is_bot
            and not self.login.endswith(("Bot", "-bot"))
            and self.login not in self.get_non_indexable_logins()
        )

    @property
    def idx_avatar_url(self) -> str:
        """Return the user's avatar URL for indexing.

        This value is used to display the user's profile image
        in search results.

        Returns:
            str: The URL of the user's avatar.
        """
        return self.avatar_url

    @property
    def idx_badge_count(self) -> int:
        """Return the number of active badges for indexing.

        This value represents how many active badges the user
        currently holds.

        Returns:
            int: The count of active user badges.
        """
        return self.user_badges.filter(is_active=True).count()

    @property
    def idx_bio(self) -> str:
        """Return the user's bio for indexing.

        This text is indexed to provide a short description
        of the user's profile.

        Returns:
            str: The user's bio.
        """
        return self.bio

    @property
    def idx_company(self) -> str:
        """Return the user's company for indexing.

        This value represents the organization or company
        the user is associated with.

        Returns:
            str: The user's company name.
        """
        return self.company

    @property
    def idx_created_at(self) -> float:
        """Return the account creation timestamp for indexing.

        The timestamp is converted to a Unix timestamp for
        storage and sorting in the search index.

        Returns:
            float: The account creation time as a Unix timestamp.
        """
        return self.created_at.timestamp()

    @property
    def idx_email(self) -> str:
        """Return the user's email for indexing.

        This value is indexed when available and allowed.

        Returns:
            str: The user's email address.
        """
        return self.email

    @property
    def idx_key(self) -> str:
        """Return the unique user key for indexing.

        The user's login is used as the unique identifier
        in the search index.

        Returns:
            str: The user's login.
        """
        return self.login

    @property
    def idx_followers_count(self) -> int:
        """Return the number of followers for indexing.

        This represents how many users follow this account.

        Returns:
            int: The follower count.
        """
        return self.followers_count

    @property
    def idx_following_count(self) -> int:
        """Return the number of accounts the user is following.

        This value represents how many other users this
        account follows.

        Returns:
            int: The following count.
        """
        return self.following_count

    @property
    def idx_location(self) -> str:
        """Return the user's location for indexing.

        This value is used for geographic filtering
        and display in search results.

        Returns:
            str: The user's location.
        """
        return self.location

    @property
    def idx_login(self) -> str:
        """Return the user's login for indexing.

        This value is used as the display and lookup
        name in the search index.

        Returns:
            str: The user's login.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """Return the user's full name for indexing.

        This value is displayed in search results
        when available.

        Returns:
            str: The user's full name.
        """
        return self.name

    @property
    def idx_public_repositories_count(self) -> int:
        """Return the number of public repositories for indexing.

        This value represents how many public repositories
        the user owns.

        Returns:
            int: The public repository count.
        """
        return self.public_repositories_count

    @property
    def idx_title(self) -> str:
        """Return the user's title for indexing.

        This may represent the user's role or professional title.

        Returns:
            str: The user's title.
        """
        return self.title

    @property
    def idx_contributions(self):
        """Return the user's repository contributions for indexing.

        This property returns a list of the user's top repository
        contributions, including repository metadata and the
        number of contributions made.

        Returns:
            list[dict]: A list of contribution data dictionaries.
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
        """Return the total number of contributions for indexing.

        This value represents the aggregate number of
        contributions made by the user.

        Returns:
            int: The contribution count.
        """
        return self.contributions_count

    @property
    def idx_issues(self) -> list[dict]:
        """Return the user's recent issues for indexing.

        This includes metadata about recently created issues
        for display and search.

        Returns:
            list[dict]: A list of issue metadata dictionaries.
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
        """Return the number of issues for indexing.

        This value represents how many issues are
        associated with the user.

        Returns:
            int: The issue count.
        """
        return self.issues.count()

    @property
    def idx_releases(self) -> list[dict]:
        """Return the user's recent releases for indexing.

        This includes metadata about releases the user
        has published.

        Returns:
            list[dict]: A list of release metadata dictionaries.
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
        """Return the number of releases for indexing.

        This value represents how many releases
        the user has published.

        Returns:
            int: The release count.
        """
        return self.releases.count()

    @property
    def idx_updated_at(self) -> float:
        """Return the last updated timestamp for indexing.

        This represents when the user's profile
        was last updated.

        Returns:
            float: The last update time as a Unix timestamp.
        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Return the user's GitHub profile URL for indexing.

        This value is used to link to the user's
        GitHub profile.

        Returns:
            str: The GitHub profile URL.
        """
        return self.url
