"""Committee API."""

from rest_framework import serializers, viewsets

from apps.owasp.models.contribute import Contribute


# Serializers define the API representation.
class ContributeSerializer(serializers.HyperlinkedModelSerializer):
    """Contribute serializer."""

    class Meta:
        model = Contribute
        fields = (
            "name",
            "description",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class ContributeViewSet(viewsets.ReadOnlyModelViewSet):
    """Contribute view set."""

    queryset = Contribute.objects.all()
    serializer_class = ContributeSerializer
