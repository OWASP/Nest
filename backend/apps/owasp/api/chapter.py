"""Chapter API."""

from rest_framework import serializers, viewsets

from apps.owasp.models import Chapter


# Serializers define the API representation.
class ChapterSerializer(serializers.HyperlinkedModelSerializer):
    """Chapter serializer."""

    class Meta:
        model = Chapter
        fields = (
            "name",
            "country",
            "region",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    """Chapter view set."""

    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
