"""Feedback API URLs."""

from rest_framework import routers

from apps.feedback.api.feedback import FeedbackViewSet

router = routers.SimpleRouter()

router.register(r"feedback", FeedbackViewSet, basename="feedback")
