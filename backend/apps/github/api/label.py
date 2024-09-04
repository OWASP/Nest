"""Label API."""

from rest_framework import serializers, viewsets

from apps.github.models import Label


# Serializers define the API representation.
class LabelSerializer(serializers.HyperlinkedModelSerializer):
    """Label serializer."""

    class Meta:
        model = Label
        fields = (
            "name",
            "description",
            "color",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class LabelViewSet(viewsets.ReadOnlyModelViewSet):
    """Label view set."""

    queryset = Label.objects.all()
    serializer_class = LabelSerializer
