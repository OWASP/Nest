"""Project API."""

from rest_framework import serializers, viewsets

from apps.owasp.models import Project


# Serializers define the API representation.
class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """Project serializer."""

    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "level",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """Project view set."""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
