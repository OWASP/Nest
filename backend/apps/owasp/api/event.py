"""Event API."""

from rest_framework import serializers, viewsets

from apps.owasp.models.event import Event


# Serializers define the API representation.
class EventSerializer(serializers.HyperlinkedModelSerializer):
    """Event serializer."""

    class Meta:
        model = Event
        fields = (
            "name",
            "description",
            "url",
        )


# ViewSets define the view behavior.
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Event view set."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
