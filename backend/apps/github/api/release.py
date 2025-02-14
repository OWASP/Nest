"""Release API."""

#!/usr/bin/env python3
from rest_framework import serializers, viewsets

from apps.github.models.release import Release


# Serializers define the API representation.
class ReleaseSerializer(serializers.HyperlinkedModelSerializer):
    """Release serializer."""

    class Meta:
        model = Release
        fields = (
            "name",
            "tag_name",
            "description",
            "created_at",
            "published_at",
        )


# ViewSets define the view behavior.
class ReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    """Release view set."""

    queryset = Release.objects.all()
    serializer_class = ReleaseSerializer
