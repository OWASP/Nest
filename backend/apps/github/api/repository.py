"""Repository API."""

#!/usr/bin/env python3
from rest_framework import serializers, viewsets

from apps.github.models.repository import Repository


# Serializers define the API representation.
class RepositorySerializer(serializers.HyperlinkedModelSerializer):
    """Repository serializer."""

    class Meta:
        model = Repository
        fields = (
            "name",
            "description",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Repository view set."""

    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
