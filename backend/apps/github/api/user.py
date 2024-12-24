"""User API with search functionality."""

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from algoliasearch_django import get_adapter

from apps.github.models.user import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """User serializer."""

    class Meta:
        model = User
        fields = (
            "name",
            "login",
            "company",
            "location",
            "created_at",
            "updated_at",
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User view set with search capabilities."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search users using Algolia.
        
        Query Parameters:
            q (str): Search query
            page (int): Page number (default: 1)
            per_page (int): Results per page (default: 20)
        """
        # Get search parameters
        query = request.query_params.get('q', '')
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 20))

        # Get Algolia adapter
        adapter = get_adapter(User)
        
        # Perform search
        results = adapter.raw_search(
            query,
            {
                'page': page - 1,  # Algolia uses 0-based pagination
                'hitsPerPage': per_page,
                'attributesToRetrieve': [
                    'idx_name',
                    'idx_login',
                    'idx_company',
                    'idx_location',
                    'idx_created_at',
                    'idx_updated_at',
                ],
            }
        )

        # Format response
        response_data = {
            'total': results['nbHits'],
            'page': page,
            'per_page': per_page,
            'total_pages': results['nbPages'],
            'results': [
                {
                    'name': hit.get('idx_name', ''),
                    'login': hit.get('idx_login', ''),
                    'company': hit.get('idx_company', ''),
                    'location': hit.get('idx_location', ''),
                    'created_at': hit.get('idx_created_at', ''),
                    'updated_at': hit.get('idx_updated_at', ''),
                }
                for hit in results['hits']
            ]
        }

        return Response(response_data)