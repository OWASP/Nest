"""Issue API."""

from rest_framework import serializers, viewsets

from apps.github.models import Issue


# Serializers define the API representation.
class IssueSerializer(serializers.HyperlinkedModelSerializer):
    """Issue serializer."""

    class Meta:
        model = Issue
        fields = (
            "title",
            "body",
            "state",
            "url",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    """Issue view set."""

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
