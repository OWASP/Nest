"""Organization API."""

#!/usr/bin/env python3
from rest_framework import serializers, viewsets

from apps.github.models.organization import Organization


# Serializers define the API representation.
class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    """Organization serializer."""

    class Meta:
        model = Organization
        fields = (
            "name",
            "login",
            "company",
            "location",
            "created_at",
            "updated_at",
        )


# ViewSets define the view behavior.
class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Organization view set."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
