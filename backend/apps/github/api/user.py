"""User API."""

from rest_framework import serializers, viewsets

from apps.github.models import User


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = (
            "name",
            "login",
            "company",
            "location",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User view set."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
