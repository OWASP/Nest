"""Github app common models."""

from django.db import models
from github.GithubException import UnknownObjectException


class GenericUserModel(models.Model):
    """Generic user model."""

    class Meta:
        abstract = True

    name = models.CharField(verbose_name="Name", max_length=200, blank=True, default="")
    login = models.CharField(verbose_name="Login", max_length=100, unique=True)
    email = models.EmailField(verbose_name="Email", max_length=100, default="", blank=True)

    avatar_url = models.URLField(verbose_name="Avatar URL", max_length=200, default="")
    company = models.CharField(verbose_name="Company", max_length=200, blank=True, default="")
    location = models.CharField(verbose_name="Location", max_length=200, default="", blank=True)

    collaborators_count = models.PositiveIntegerField(
        verbose_name="Collaborators count", default=0
    )
    following_count = models.PositiveIntegerField(verbose_name="Following count", default=0)
    followers_count = models.PositiveIntegerField(verbose_name="Followers count", default=0)
    public_gists_count = models.PositiveIntegerField(verbose_name="Public gists count", default=0)
    public_repositories_count = models.PositiveIntegerField(
        verbose_name="Public repositories count", default=0
    )

    created_at = models.DateTimeField(verbose_name="Created at")
    updated_at = models.DateTimeField(verbose_name="Updated at")

    @property
    def nest_key(self):
        """Nest key."""
        return self.login

    @property
    def title(self) -> str:
        """Entity title."""
        return (
            f"{self.name} ({self.login})" if self.name and self.name != self.login else self.login
        )

    @property
    def url(self) -> str:
        """Entity URL."""
        return f"https://github.com/{self.login.lower()}"

    def from_github(self, data) -> None:
        """Update instance based on GitHub data."""
        field_mapping = {
            "avatar_url": "avatar_url",
            "collaborators_count": "collaborators",
            "company": "company",
            "created_at": "created_at",
            "email": "email",
            "followers_count": "followers",
            "following_count": "following",
            "location": "location",
            "login": "login",
            "name": "name",
            "public_gists_count": "public_gists",
            "public_repositories_count": "public_repos",
            "updated_at": "updated_at",
        }

        # Direct fields.
        for model_field, gh_field in field_mapping.items():
            value = getattr(data, gh_field)
            if value is not None:
                setattr(self, model_field, value)


class NodeModel(models.Model):
    """Node model."""

    class Meta:
        abstract = True

    node_id = models.CharField(verbose_name="Node ID", unique=True)

    @staticmethod
    def get_node_id(node):
        """Extract node_id."""
        try:
            return node.raw_data["node_id"]
        except UnknownObjectException:
            pass
