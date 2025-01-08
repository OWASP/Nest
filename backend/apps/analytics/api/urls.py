"""Analytics API URLs."""

from rest_framework import routers

from apps.analytics.api.usersearchquery import UserSearchQueryViewSet

router = routers.SimpleRouter()

router.register(r"analytics/search", UserSearchQueryViewSet)
