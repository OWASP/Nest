"""GitHub user GraphQL node."""

import graphene

from apps.common.graphql.nodes import BaseNode
from apps.github.models.user import User


class UserNode(BaseNode):
    """GitHub user node."""

    avatar_url = graphene.String()
    bio = graphene.String()
    company = graphene.String()
    contributions_count = graphene.Int()  # Important
    created_at = graphene.Float()
    email = graphene.String()
    followers_count = graphene.Int()
    following_count = graphene.Int()
    key = graphene.String()
    location = graphene.String()
    login = graphene.String()
    name = graphene.String()
    public_repositories_count = graphene.Int()
    title = graphene.String()
    updated_at = graphene.Float()
    url = graphene.String()

    class Meta:
        model = User
        fields = ("avatar_url", "email", "id", "login", "name")

    def resolve_avatar_url(self, info):
        """Resolve user avatar URL."""
        return self.idx_avatar_url

    def resolve_bio(self, info):
        """Resolve user bio."""
        return self.idx_bio

    def resolve_company(self, info):
        """Resolve user company."""
        return self.idx_company

    def resolve_contributions_count(self, info):
        """Resolve user contributions count."""
        return self.contributions_count

    def resolve_created_at(self, info):
        """Resolve user created at."""
        return self.idx_created_at

    def resolve_email(self, info):
        """Resolve user email."""
        return self.idx_email

    def resolve_followers_count(self, info):
        """Resolve user followers count."""
        return self.idx_followers_count

    def resolve_following_count(self, info):
        """Resolve user following count."""
        return self.idx_following_count

    def resolve_key(self, info):
        """Resolve user key."""
        return self.idx_key

    def resolve_location(self, info):
        """Resolve user location."""
        return self.idx_location

    def resolve_login(self, info):
        """Resolve user login."""
        return self.idx_login

    def resolve_name(self, info):
        """Resolve user name."""
        return self.idx_name

    def resolve_public_repositories_count(self, info):
        """Resolve user public repositories count."""
        return self.idx_public_repositories_count

    def resolve_title(self, info):
        """Resolve user title."""
        return self.idx_title

    def resolve_updated_at(self, info):
        """Resolve user updated at."""
        return self.idx_updated_at

    def resolve_url(self, info):
        """Resolve user URL."""
        return self.idx_url
