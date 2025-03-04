"""GitHub user model mixins for index-related functionality."""

from apps.github.models.organization import Organization
from apps.github.models.repository_contributor import RepositoryContributor
from django.db.models import Sum

ISSUES_LIMIT = 6
RELEASES_LIMIT = 6
TOP_REPOSITORY_CONTRIBUTORS_LIMIT = 6


class UserIndexMixin:
    """User index mixin."""

    @property
    def is_indexable(self):
        """Users to index."""
        return (
            self.login != "ghost"  # See https://github.com/ghost for more info.
            and self.login not in Organization.get_logins()
        )

    @property
    def idx_avatar_url(self):
        """Return avatar URL for indexing."""
        return self.avatar_url

    @property
    def idx_bio(self):
        """Return bio for indexing."""
        return self.bio

    @property
    def idx_company(self):
        """Return company for indexing."""
        return self.company

    @property
    def idx_created_at(self):
        """Return created at timestamp for indexing."""
        return self.created_at.timestamp()

    @property
    def idx_email(self):
        """Return email for indexing."""
        return self.email

    @property
    def idx_key(self):
        """Return key for indexing."""
        return self.login

    @property
    def idx_followers_count(self):
        """Return followers count for indexing."""
        return self.followers_count

    @property
    def idx_following_count(self):
        """Return following count for indexing."""
        return self.following_count

    @property
    def idx_location(self):
        """Return location for indexing."""
        return self.location

    @property
    def idx_login(self):
        """Return login for indexing."""
        return self.login

    @property
    def idx_name(self):
        """Return name for indexing."""
        return self.name

    @property
    def idx_public_repositories_count(self):
        """Return public repositories count for indexing."""
        return self.public_repositories_count

    @property
    def idx_title(self):
        """Return title for indexing."""
        return self.title

    @property
    def idx_contributions(self):
        """Return contributions for indexing."""
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
            for rc in RepositoryContributor.objects.filter(user=self)
            .order_by("-contributions_count")
            .select_related("repository")[:TOP_REPOSITORY_CONTRIBUTORS_LIMIT]
        ]

    @property
    def idx_contributions_count(self):
        """Return contributions count for indexing."""
        counts =  RepositoryContributor.objects.filter(user=self).aggregate(total_contributions=Sum('contributions_count'))['total_contributions']
        return counts if counts else 0

    @property
    def idx_issues(self):
        """Return issues for indexing."""
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
            }
            for i in self.issues.select_related(
                "repository",
                "repository__owner",
            ).order_by("-created_at")[:ISSUES_LIMIT]
        ]

    @property
    def idx_issues_count(self):
        """Return issues count for indexing."""
        return self.issues.count()

    @property
    def idx_releases(self):
        """Return releases for indexing."""
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
            }
            for r in self.releases.select_related(
                "repository",
                "repository__owner",
            ).order_by("-published_at")[:RELEASES_LIMIT]
        ]

    @property
    def idx_releases_count(self):
        """Return releases count for indexing."""
        return self.releases.count()

    @property
    def idx_updated_at(self):
        """Return updated at timestamp for indexing."""
        return self.updated_at.timestamp()

    @property
    def idx_url(self):
        """Return GitHub profile URL for indexing."""
        return self.url
