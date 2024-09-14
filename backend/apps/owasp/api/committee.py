"""Committee API."""

from rest_framework import serializers, viewsets

from apps.owasp.models.committee import Committee


# Serializers define the API representation.
class CommitteeSerializer(serializers.HyperlinkedModelSerializer):
    """Committee serializer."""

    class Meta:
        model = Committee
        fields = (
            "name",
            "description",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    """Committee view set."""

    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
