"""User API."""

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.github.models.user import User


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = (
            "avatar_url",
            "bio",
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


# ViewSets define the view behavior.
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=["get"], url_path="login/(?P<login>[^/.]+)")
    def get_user_by_login(self, request, login=None):
        """Retrieve a user by their login.

        Args:
            request (Request): The HTTP request object.
            login (str, optional): The login of the user to retrieve.

        Returns:
            Response: The serialized user data or a 404 error if the user is not found.

        """
        try:
            user = User.objects.get(login=login)
            serializer = self.get_serializer(user)
            data = serializer.data
            return Response(data)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)
