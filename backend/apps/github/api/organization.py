"""Organization API."""

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

    queryset = Organization.objects.filter(is_owasp_organization=True)
    serializer_class = OrganizationSerializer
