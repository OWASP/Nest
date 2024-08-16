"""Repository app models."""

from django.db import models

from apps.common.models import TimestampedModel


class Repository(TimestampedModel):
    """Repository model."""

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "platform"], name="unique_name_platform"),
        ]
        db_table = "repositories"

    class OwnerType(models.TextChoices):
        ORGANIZATION = "organization", "Organization"
        USER = "user", "User"

    class Platforms(models.TextChoices):
        GITHUB = "github", "GitHub"

    name = models.CharField(verbose_name="Name", max_length=100)
    description = models.CharField(verbose_name="Description", max_length=500, default="")

    is_archived = models.BooleanField(verbose_name="Is archived", default=False)
    is_fork = models.BooleanField(verbose_name="Is fork", default=False)

    forks_count = models.PositiveIntegerField(verbose_name="Forks count", default=0)
    open_issues_count = models.PositiveIntegerField(verbose_name="Open issues count", default=0)
    stars_count = models.PositiveIntegerField(verbose_name="Stars count", default=0)
    subscribers_count = models.PositiveIntegerField(verbose_name="Subscribers count", default=0)

    language = models.CharField(verbose_name="Language", max_length=50, default="")
    size = models.PositiveIntegerField(verbose_name="Size in KB", default=0)

    platform = models.CharField(
        verbose_name="Platform", max_length=10, choices=Platforms.choices, default=Platforms.GITHUB
    )
    platform_created_at = models.DateTimeField(verbose_name="Repository created time")
    platform_pushed_at = models.DateTimeField(verbose_name="Repository last pushed time")
    platform_updated_at = models.DateTimeField(verbose_name="Repository last updated time")

    owner_login = models.CharField(verbose_name="Owner login", max_length=100, default="")
    owner_type = models.CharField(
        verbose_name="Owner type", max_length=20, choices=OwnerType.choices, default=OwnerType.USER
    )

    def __str__(self):
        """Repository human readable representation."""
        return f"{self.name}"

    @property
    def owasp_url(self):
        """Get OWASP URL for the repository."""
        return f"https://owasp.org/{self.name}"

    def from_github_response(self, response):
        """Update instance based on GitHub API response data."""
        self.description = response.description
        self.is_archived = response.archived
        self.is_fork = response.fork

        self.forks_count = response.forks_count

        self.platform_created_at = response.created_at
        self.platform_pushed_at = response.pushed_at
        self.platform_updated_at = response.updated_at
