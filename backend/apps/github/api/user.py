"""User API."""

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.github.models.user import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""
    
    # Use the indexed data instead of direct model relationships
    issues = serializers.SerializerMethodField()
    releases = serializers.SerializerMethodField()
    issues_count = serializers.IntegerField(source='idx_issues_count')
    releases_count = serializers.IntegerField(source='idx_releases_count')

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "bio",
            "issues",
            "releases",
            "issues_count",
            "releases_count",
            "company",
            "email",
            "followers_count",
            "following_count",
            "location",
            "login",
            "name",
            "public_repositories_count",
            "title",
            "twitter_username",
            "url",
            "created_at",
            "updated_at",
        )

    def get_issues(self, obj):
        """Get issues from indexed data."""
        return obj.idx_issues

    def get_releases(self, obj):
        """Get releases from indexed data."""
        return obj.idx_releases


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["get"], url_path="login/(?P<login>[^/.]+)")
    def get_user_by_login(self, request, login=None):
        """Get user by login."""
        try:
            user = User.objects.get(login=login)
            serializer = self.get_serializer(user)
            data = serializer.data
            return Response(data)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)