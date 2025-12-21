"""GitHub user model mixins for index-related functionality."""

from django.db.models import Q

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin."""

    @property
    def is_indexable(self):
        """Determine if the user is indexable.

        Returns:
            bool: True if the user is not a bot and has an indexable login, False otherwise.
        """
        return (
            not self.is_bot
            and not self.login.endswith(("Bot", "-bot"))
            and self.login not in self.get_non_indexable_logins()
        )

    @property
    def idx_avatar_url(self) -> str:
        """Return the avatar URL for indexing.

        Returns:
            str: The URL of the user's avatar.
        """
        return self.avatar_url

    @property
    def idx_badge_count(self) -> int:
        """Return the active badge count for indexing.

        Returns:
            int: The number of active badges the user has.
        """
        return self.user_badges.filter(is_active=True).count()

    @property
    def idx_bio(self) -> str:
        """Return the bio for indexing.

        Returns:
            str: The user's biography.
        """
        return self.bio

    @property
    def idx_company(self) -> str:
        """Return the company for indexing.

        Returns:
            str: The name of the user's company.
        """
        return self.company

    @property
    def idx_created_at(self) -> float:
        """Return the created at timestamp for indexing.

        Returns:
            float: The creation timestamp of the user profile.
        """
        return self.created_at.timestamp()

    @property
    def idx_email(self) -> str:
        """Return the email for indexing.

        Returns:
            str: The user's email address.
        """
        return self.email

    @property
    def idx_key(self) -> str:
        """Return the key (login) for indexing.

        Returns:
            str: The login name of the user.
        """
        return self.login

    @property
    def idx_followers_count(self) -> int:
        """Return the followers count for indexing.

        Returns:
            int: The number of followers the user has.
        """
        return self.followers_count

    @property
    def idx_following_count(self) -> int:
        """Return the following count for indexing.

        Returns:
            int: The number of users the user is following.
        """
        return self.following_count

    @property
    def idx_location(self) -> str:
        """Return the location for indexing.

        Returns:
            str: The user's location.
        """
        return self.location

    @property
    def idx_login(self) -> str:
        """Return the login for indexing.

        Returns:
            str: The user's login name.
        """
        return self.login

    @property
    def idx_name(self) -> str:
        """Return the name for indexing.

        Returns:
            str: The user's name.
        """
        return self.name

    @property
    def idx_public_repositories_count(self) -> int:
        """Return the public repositories count for indexing.

        Returns:
            int: The number of public repositories owned by the user.
        """
        return self.public_repositories_count

    @property
    def idx_title(self) -> str:
        """Return the title for indexing.

        Returns:
            str: The user's title.
        """
        return self.title

    @property
    def idx_contributions(self):
        """Return formatted contributions for indexing.

        Returns:
            list[dict]: A list of dictionaries containing contribution details for top repositories.
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
        """Return the total contributions count for indexing.

        Returns:
            int: The total number of contributions.
        """
        return self.contributions_count

    @property
    def idx_issues(self) -> list[dict]:
        """Return recent issues for indexing.

        Returns:
            list[dict]: A list of dictionaries containing details of the user's recent issues.
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
        """Return the total issues count for indexing.

        Returns:
            int: The total number of issues the user is associated with.
        """
        return self.issues.count()

    @property
    def idx_releases(self) -> list[dict]:
        """Return recent releases for indexing.

        Returns:
            list[dict]: A list of dictionaries containing details of the user's recent releases.
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
        """Return the total releases count for indexing.

        Returns:
            int: The total number of releases the user is associated with.
        """
        return self.releases.count()

    @property
    def idx_updated_at(self) -> float:
        """Return the updated at timestamp for indexing.

        Returns:
            float: The last update timestamp of the user profile.
        """
        return self.updated_at.timestamp()

    @property
    def idx_url(self) -> str:
        """Return the GitHub profile URL for indexing.

        Returns:
            str: The URL of the user's GitHub profile.
        """
        return self.url
