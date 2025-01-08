"""UserSearcQuery API."""

from rest_framework import serializers, viewsets
from rest_framework.permissions import AllowAny

from apps.analytics.models.usersearchquery import UserSearchQuery


# Serializers define the API representation.
class UserSearchQuerySerializer(serializers.HyperlinkedModelSerializer):
    """UserSearchQuery serializer."""

    class Meta:
        model = UserSearchQuery
        fields = "__all__"


# ViewSets define the view behavior.
class UserSearchQueryViewSet(viewsets.ModelViewSet):
    """UserSearchQuery view set."""

    queryset = UserSearchQuery.objects.all()
    serializer_class = UserSearchQuerySerializer
    permission_classes = [AllowAny]
