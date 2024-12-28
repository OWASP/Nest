"""GitHub user API endpoints and serializers."""

from algoliasearch_django import get_adapter
from rest_framework import pagination, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.github.models.user import User


class UserPagination(pagination.PageNumberPagination):
    """Pagination class for User model."""

    page_size = 20
    page_size_query_param = "per_page"
    max_page_size = 100


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = (
            "name",
            "login",
            "bio",
            "avatar_url",
            "company",
            "location",
            "email",
            "public_repositories_count",
            "followers_count",
            "following_count",
            "created_at",
            "updated_at",
            "type",
            "url",
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User model."""

    queryset = User.objects.all().order_by("login")
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_queryset(self):
        """Get the queryset for the view."""
        return super().get_queryset().order_by("login")

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search users using Algolia."""
        query = request.query_params.get("q", "")
        page = int(request.query_params.get("page", 1))
        per_page = min(
            int(request.query_params.get("per_page", 20)), self.pagination_class.max_page_size
        )

        adapter = get_adapter(User)
        results = adapter.raw_search(
            query,
            {
                "page": page - 1,
                "hitsPerPage": per_page,
                "attributesToRetrieve": [
                    "idx_name",
                    "idx_login",
                    "idx_bio",
                    "idx_avatar_url",
                    "idx_company",
                    "idx_location",
                    "idx_email",
                    "idx_public_repositories_count",
                    "idx_followers_count",
                    "idx_following_count",
                    "idx_created_at",
                    "idx_updated_at",
                    "idx_type",
                    "idx_url",
                ],
            },
        )

        response_data = {
            "count": results["nbHits"],
            "results": [
                {
                    "name": hit.get("idx_name", ""),
                    "login": hit.get("idx_login", ""),
                    "bio": hit.get("idx_bio", ""),
                    "avatar_url": hit.get("idx_avatar_url", ""),
                    "company": hit.get("idx_company", ""),
                    "location": hit.get("idx_location", ""),
                    "email": hit.get("idx_email", ""),
                    "public_repositories_count": hit.get("idx_public_repositories_count", 0),
                    "followers_count": hit.get("idx_followers_count", 0),
                    "following_count": hit.get("idx_following_count", 0),
                    "created_at": hit.get("idx_created_at", ""),
                    "updated_at": hit.get("idx_updated_at", ""),
                    "type": hit.get("idx_type", ""),
                    "url": hit.get("idx_url", ""),
                }
                for hit in results["hits"]
            ],
        }

        return Response(response_data)
